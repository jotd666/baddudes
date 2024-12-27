from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib

this_dir = pathlib.Path(__file__).absolute().parent

data_dir = os.path.join(this_dir,"..","..","data")
src_dir = os.path.join(this_dir,"..","..","src","amiga")

for i in range(2):
    dude_pic = this_dir / f"dudes_{i}.png"
    p = PIL.Image.open(dude_pic)