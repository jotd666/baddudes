from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib

this_dir = pathlib.Path(__file__).absolute().parent

data_dir = this_dir / ".." / ".." / "data"
src_dir = this_dir / ".." / ".." / "src" / "amiga"

with open(src_dir / "dudes.68k","w") as f:
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

        f.write(f"\tdc.w\t{x_start},{y_start},{width},{height}\n")
        p = bitplanelib.palette_extract(rval)
        p.remove(transparent)
        p.insert(0,transparent)
        f.write("; palette\n")
        bitplanelib.palette_dump(p,f)
        f.write("; bitmap\n")
        raw = bitplanelib.palette_image2raw(rval,None,p,mask_color=transparent)
        bitplanelib.dump_asm_bytes(raw,f)

