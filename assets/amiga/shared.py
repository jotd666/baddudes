from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib

this_dir = pathlib.Path(__file__).absolute().parent

data_dir = this_dir / ".." / ".." / "data"
src_dir = this_dir / ".." / ".." / "src" / "amiga"
whole_pics_dir = this_dir / "whole_pics"
generated_src_dir = src_dir / "generated"
sheets_path = this_dir / ".." / "sheets"
dump_dir = this_dir / "dumps"

transparent = (255,0,255)

def asm2bin(source,dest):
    subprocess.run(["vasmm68k_mot","-nosym","-pic","-Fbin",source,"-o",dest],check=True)

def transparent_first(palette,transparent):
    # re-insert transparent in first position
    palette.remove(transparent)
    palette.insert(0,transparent)

def palette_pad(palette,pad_nb):
    palette += (pad_nb-len(palette)) * [(0x10,0x20,0x30)]

def ensure_empty(d):
    if os.path.exists(d):
        for f in os.listdir(d):
            os.remove(os.path.join(d,f))
    else:
        os.makedirs(d)