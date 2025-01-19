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
        reduced_colors_truck1_img = truck1_img.quantize(colors=8,dither=0).convert('RGB')
        truck1_palette = bitplanelib.palette_extract(reduced_colors_truck1_img)
        transparent_first(truck1_palette,transparent)

        color_replacement_dict = bitplanelib.closest_colors_replacement_dict(truck1_palette,global_palette)
        color_replacement_dict.pop(transparent)
        bitplanelib.replace_color_from_dict(reduced_colors_truck1_img,color_replacement_dict)

        reduced_palette = bitplanelib.palette_extract(reduced_colors_truck1_img)

        raw = bitplanelib.palette_image2raw(reduced_colors_truck1_img,None,global_palette,generate_mask=True,mask_color=transparent)

        nb_planes = 7
        width,height = reduced_colors_truck1_img.size
        # width in even bytes, plus 16 bit shift
        width = width//8 + 2
        if width % 2:
            width += 1

        with open(asm_out,"w") as f:


            f.write(f"\tdc.w\t{nb_planes},{width},{height}   ; nb planes, width in bytes, height\n")


            plane_size = len(raw)//nb_planes # mask included
            f.write(f"; bpldata (plane size = {plane_size})\n")
            offset = 0
            for j in range(nb_planes):
                f.write(f"truck_plane_{j}:\n")
                block = raw[offset:offset+plane_size]
                if any(block):
                    bitplanelib.dump_asm_bytes(block,f)
                else:
                    print("zerooooes",j)
                offset += plane_size


        #asm2bin(asm_out,dudes_bin)
        reduced_palette.remove(transparent)
        return reduced_palette

if __name__ == "__main__":
    gp = [(0, 0, 0),
 (34, 34, 34),
 (56, 34, 0),
 (56, 34, 17),
 (56, 56, 34),
 (56, 56, 56),
 (56, 71, 90),
 (56, 104, 123),
 (71, 34, 0),
 (71, 56, 0),
 (71, 56, 34),
 (71, 56, 56),
 (71, 71, 34),
 (71, 71, 64),
 (71, 90, 104),
 (90, 56, 0),
 (90, 71, 17),
 (90, 71, 56),
 (90, 71, 71),
 (90, 90, 71),
 (90, 90, 90),
 (90, 104, 123),
 (97, 71, 0),
 (104, 104, 97),
 (104, 123, 142),
 (114, 90, 64),
 (123, 104, 90),
 (123, 123, 123),
 (142, 56, 17),
 (142, 104, 56),
 (142, 123, 104),
 (159, 123, 71)]
    reduced = doit(global_palette=gp,force=True)
