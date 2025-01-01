from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib

from shared import *


asm_out = src_dir / "generated" / "dudes.68k"

pad_value =(0X10,0x20,0x30)
with open(asm_out,"w") as f:
    f.write("main_table:\n")
    for i in range(2):
        f.write(f"\tdc.l\tdude_{i}-main_table\n")

    for i in range(2):
        dude_pic = this_dir / f"dudes_{i}.png"
        f.write(f"dude_{i}:\n")
        p = Image.open(dude_pic)
        transparent = p.getpixel((0,0))
        x_start,rval = bitplanelib.autocrop_x(p,transparent,align=16)
        y_start,rval = bitplanelib.autocrop_y(rval,transparent)
        width = rval.size[0]
        height = rval.size[1]
        f.write("; x  y  w  h\n")
        f.write(f"\tdc.w\t{x_start},{y_start+8},{width},{height}\n")
        p = bitplanelib.palette_extract(rval,pad_count=32,pad_value=pad_value)
        p.remove(transparent)
        p.insert(0,transparent)

        f.write("; partial upper palette\n")
        bitplanelib.palette_dump([(0,0,0)]+p[1:],f) # black will not trigger flashes
        f.write("; bitplanes\n")
        nb_planes = 6
        for j in range(nb_planes):
            f.write(f"\tdc.l\tdude_{i}_plane_{j}-dude_{i}\n")

        # generate bitplanes, but with high palette (shifted by 32 colors) so we can mix with
        # tile base colors
        palette_64 = (32*[pad_value]) + p

        raw = bitplanelib.palette_image2raw(rval,None,palette_64,mask_color=transparent)
        plane_size = len(raw)//nb_planes
        f.write(f"; bpldata (plane size = {plane_size})\n")
        offset = 0
        for j in range(nb_planes):
            f.write(f"dude_{i}_plane_{j}:\n")
            bitplanelib.dump_asm_bytes(raw[offset:offset+plane_size],f)
            offset += plane_size

dudes_bin = data_dir / "dudes.bin"

asm2bin(asm_out,dudes_bin)

