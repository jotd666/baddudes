from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib

from shared import *


def doit(global_palette,force=False):
    asm_out = generated_src_dir / "truck_1.68k"
    dudes_bin = data_dir / "truck_1.bin"
    if force or not dudes_bin.exists():
        pad_value =(0X10,0x20,0x30)
        truck1_img = Image.open(whole_pics_dir / "truck_1.png")
        y_start = 352
        width = 16*24
        truck1_img=truck1_img.crop((0,y_start,width,y_start+128))
        forced_nb_planes = 3
        reduced_nb_colors = 1<<forced_nb_planes

        # remove some rows to show the upper iron bar (lame trick)
        bar_height = 8
        bar_start = 32
        for x in range(truck1_img.size[0]):
            for y in range(bar_start,bar_start+bar_height):
                truck1_img.putpixel((x,y),transparent)


        reduced_colors_truck1_img = truck1_img.quantize(colors=reduced_nb_colors,dither=0).convert('RGB')
        truck1_palette = bitplanelib.palette_extract(reduced_colors_truck1_img)
        transparent_first(truck1_palette,transparent)

        color_replacement_dict = bitplanelib.closest_colors_replacement_dict(truck1_palette,global_palette)
        color_replacement_dict.pop(transparent)
        bitplanelib.replace_color_from_dict(reduced_colors_truck1_img,color_replacement_dict)

        reduced_palette = bitplanelib.palette_extract(reduced_colors_truck1_img)
        if len(reduced_palette) < reduced_nb_colors:
            reduced_palette += [(0x10,0x20,0x30)]*(len(reduced_palette) - reduced_nb_colors)
        raw = bitplanelib.palette_image2raw(reduced_colors_truck1_img,None,reduced_palette,forced_nb_planes=forced_nb_planes,
        generate_mask=True,blit_pad=True,mask_color=transparent)

        nb_planes = 4
        real_width,height = reduced_colors_truck1_img.size
        # width in even bytes, plus 16 bit shift
        width = real_width//8 + 2
        if width % 2:
            width += 1

        plane_size = len(raw)//nb_planes # mask included


        if width*height != plane_size:
            raise Error(f"Computed w*h = {width}*{height} != plane size ({plane_size})")
        with open(asm_out,"w") as f:


            f.write(f"\tdc.w\t{nb_planes},{width},{height}   ; nb planes (with mask), width in bytes (real width = {real_width}), height\n")



            f.write(f"; bpldata (plane size = {plane_size})\n")
            offset = 0
            f.write("main_table:\n")
            # make it suitable for 6 plane display
            for j in range(nb_planes-1):
                f.write(f"\tdc.l    truck_plane_{j}-main_table\n")
            for j in range(7-nb_planes):
                f.write("\tdc.l\t0\n")
            f.write(f"\tdc.l    truck_plane_{nb_planes-1}-main_table\n")
            for j in range(nb_planes):
                f.write(f"truck_plane_{j}:\n")
                block = raw[offset:offset+plane_size]
                if any(block):
                    bitplanelib.dump_asm_bytes(block,f)
                else:
                    raise Exception("zero plane!")
                offset += plane_size


        asm2bin(asm_out,dudes_bin)
        reduced_palette.remove(transparent)
        return reduced_palette

if __name__ == "__main__":
    gp = [(0, 0, 0),
 (56, 71, 90),
 (71, 90, 104),
 (104, 104, 97),
 (123, 123, 123),
 (142, 56, 17),
 (34, 34, 34),
 (56, 34, 0),
 (56, 34, 17),
 (56, 56, 34),
 (56, 56, 56),
 (56, 104, 123),
 (71, 34, 0),
 (71, 56, 0),
 (71, 56, 34),
 (71, 56, 56),
 (71, 71, 34),
 (71, 71, 64),
 (90, 56, 0),
 (90, 71, 17),
 (90, 71, 56),
 (90, 71, 71),
 (90, 90, 71),
 (90, 90, 90),
 (90, 104, 123),
 (97, 71, 0),
 (104, 123, 142),
 (114, 90, 64),
 (123, 104, 90),
 (142, 104, 56),
 (142, 123, 104),
 (159, 123, 71)]
    reduced = doit(global_palette=gp,force=True)
