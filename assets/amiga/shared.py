from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib

this_dir = pathlib.Path(__file__).absolute().parent

data_dir = this_dir / ".." / ".." / "data"
src_dir = this_dir / ".." / ".." / "src" / "amiga"
whole_pics_dir = this_dir / "whole_pics"
generated_src_dir = src_dir / "generated"
sheets_path = this_dir / ".." / "sheets"
dump_dir = this_dir / "dumps"

used_sprite_cluts_file = this_dir / "used_sprite_cluts.json"
used_tile_cluts_file = this_dir / "used_tile_cluts.json"
used_graphics_dir = this_dir / "used_graphics"

transparent = (255,0,255)

def load_grouped_dicts():

    # ATM manual lateral grouping of sprites (possibly already vertically grouped)
    # those are manual, but with the help of frame decode (sprite_decode.py) which analyzes
    # the whole set of game macro-objects
    with open(this_dir / "macro_grouped_sprites.json") as f:
        # load and convert to easily useable
        gd = json.load(f)
        side_grouped_dict,vert_grouped_dict = [{int(k,16):[int(c,16) for c in v]
                        if isinstance(v,list) else [int(v,16)] for k,v in gd[x].items()}
                        for x in ["horizontal","vertical"]]
    return side_grouped_dict,vert_grouped_dict

def asm2bin(source,dest):
    subprocess.run(["vasmm68k_mot","-nosym","-pic","-Fbin",source,"-o",dest],check=True,stdout=subprocess.DEVNULL)

def transparent_first(palette,transparent):
    # re-insert transparent in first position
    palette.remove(transparent)
    palette.insert(0,transparent)

def palette_pad(palette,pad_nb):
    palette += (pad_nb-len(palette)) * [(0x10,0x20,0x30)]

def ensure_empty(d):
    if os.path.exists(d):
        for f in os.listdir(d):
            x = os.path.join(d,f)
            if os.path.isfile(x):
                os.remove(x)
    else:
        os.makedirs(d)

def ensure_exists(d):
    if os.path.exists(d):
        pass
    else:
        os.makedirs(d)