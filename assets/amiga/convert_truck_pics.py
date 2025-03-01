from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib

from shared import *

empty_plane_workaround = True

def doit(global_palette,name,y_start,level_1_bar,exhaust_height,width,height,wheels_height,y_pos,forced_nb_planes):
    asm_out = generated_src_dir / f"{name}.68k"
    dudes_bin = data_dir / f"{name}.bin"

    if True:
        pad_value =(0X10,0x20,0x30)
        truck1_img = Image.open(whole_pics_dir / f"{name}.png")

        truck1_img=truck1_img.crop((0,y_start+exhaust_height,width,y_start+height))

        truck1_img.save(dump_dir/f"{name}.png")

        reduced_nb_colors = 1<<forced_nb_planes

        if forced_nb_planes>4:
            # could work with 32 colors but would take too much memory and blitter bandwidth
            raise Exception("max number of planes for trucks/train is 4")
        if empty_plane_workaround:
            forced_nb_planes = 4

        if level_1_bar:
            # remove some rows to show the upper iron bar (lame trick)
            bar_height = 8
            bar_start = 16
            for x in range(truck1_img.size[0]):
                for y in range(bar_start,bar_start+bar_height):
                    truck1_img.putpixel((x,y),transparent)



        reduced_colors_truck1_img = truck1_img.quantize(colors=reduced_nb_colors,dither=0).convert('RGB')
        # restore the transparent color afterwards (transparent may have been quantized too), we know that top right
        # pixel is "empty" so whatever color is there is the replacement for transparent
        changed_transparent = reduced_colors_truck1_img.getpixel((reduced_colors_truck1_img.size[0]-1,0))

        bitplanelib.replace_color(reduced_colors_truck1_img,{changed_transparent},transparent)
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

        nb_planes = forced_nb_planes+1
        real_width,height = reduced_colors_truck1_img.size
        # width in even bytes, plus 16 bit shift
        width = real_width//8 + 2
        if width % 2:
            width += 1

        plane_size = len(raw)//nb_planes # mask included


        if width*height != plane_size:
            raise Exception(f"Computed w*h = {width}*{height} != plane size ({plane_size})")
        with open(asm_out,"w") as f:


            f.write(f"\tdc.w\t7,{width},{height},{y_pos},{wheels_height}   ; nb planes (with mask), width in bytes (real width = {real_width}), height, ypos, wheel height\n")



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
                if any(block) or empty_plane_workaround:
                    bitplanelib.dump_asm_bytes(block,f)
                else:
                    raise Exception("zero plane!")
                offset += plane_size


        asm2bin(asm_out,dudes_bin)
        reduced_palette.remove(transparent)
        return reduced_palette

def doit_truck_1(global_palette,nb_planes):
    return doit(global_palette,name="truck_1",level_1_bar=True,
forced_nb_planes=nb_planes,y_start=352,height=128,exhaust_height=16,width=16*24,wheels_height=32,y_pos = 16*23)

def doit_truck_2(global_palette,nb_planes):
    return doit(global_palette,name="truck_2",level_1_bar=False,forced_nb_planes=nb_planes,
    y_start=352,height=128-16,exhaust_height=16,width=544+8,wheels_height=16,   # save 16 pixels, animated sprite wheels cover the lower part!
    y_pos = 16*23 - 256)

def doit_train(global_palette,nb_planes):
    return doit(global_palette,name="train",level_1_bar=False,forced_nb_planes=nb_planes,
    y_start=96+16,height=64+48,exhaust_height=0,width=1920+256,wheels_height=16,
    y_pos = 96+16)

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
    reduced = doit_truck_1(global_palette=gp,nb_planes=3)
