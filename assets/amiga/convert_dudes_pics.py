from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib

this_dir = pathlib.Path(__file__).absolute().parent

data_dir = os.path.join(this_dir,"..","..","data")
src_dir = os.path.join(this_dir,"..","..","src","amiga")

for i in range(2):
    dude_pic = this_dir / f"dudes_{i}.png"
    p = Image.open(dude_pic)
    transparent = p.getpixel((0,0))
    x_start,rval = bitplanelib.autocrop_x(p,transparent,align=16)
    y_start,rval = bitplanelib.autocrop_y(rval,transparent)
    print(x_start,y_start)
    rval.save(this_dir/ f"dudes_crop_{i}.png")
