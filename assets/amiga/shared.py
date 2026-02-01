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
multi_dual_sprite_tiles_file = this_dir / "multi_dual_sprite_tiles.json"

transparent = (255,0,255)
impossible_color = (0x10,0x20,0x30)

player_frames = {0x008,0x00a,0x00c,0x00d,0x00e,0x010,0x012,0x014,0x016,0x018,0x01a,0x01c,
0x01e,0x020,0x022,0x026,0x02a,0x02c,0x02e,0x034,0x035,0x036,0x038,0x040,0x044,
0x046,0x047,0x048,0x04c,0x050,0x058,0x05a,0x05c,0x05d,0x05e,0x060,0x068,0x9,0x9A,0x9C,0x9D,0x9E,
0x069,0x06a,0x06a,0x06b,0x06c,0x06d,0x070,0x070,0x071,0x072,0x072,0x073,0x074,0x3C,
0x075,0x078,0x07c,0x080,0x088,0x08a,0x08c,0x090,0x094,0x0a8,0x0b0,0x0b2,0x0b4,
0x0bc,0x0c0,0x0c8,0x0cc,0x0d0,0x0d2,0x0d6,0x0d8,0x0da,0x0e0,0x0e4,0x0e6,0x0ea,
0x0ee,0x0f0,0x0f2,0x0f4,0x0f6,0x0f8,0x0fc,0x0fe,0x100,0x102,0x108,0x109,0x10a,
0x10c,0x110,0x114,0x116,0x118,0x11a,0x11c,0x11e,0x120,0x122,0x126,0x138,0x13a,
0x13c,0x13d,0x14a,0x14c,0x150,0x152,0x158,0x15a,0x15d,0x15f,0x160,0x163,0x164,0x30,0x32,
0x165,0x166,0x167,0x168,0x169,0x16a,0x16e,0x16f,0x170,0x172,0x180,0x184,0x186,0x028,
0x188,0x18c,0x190,0x192,0x193,0x194,0x19c,0x1a0,0x1a2,0x1c0,0x1c1,0x1c2,0x1c3,0x19e,
0x1c4,0x1c8,0x1ca,0x1d0,0x1d2,0x1db,0x1dc,0x1dd,0x1de,0x1e1,0x1e2,0x1e6,0x1f0,0x1f2,0x1f3,0x1f4,0x1f5,
0x1f6,0x1f8,0x1fb,0x1fc,0x800,0x804,0x805,0x806,0x80a,0x80c,0x810,0x812,0x813,0x815}

def get_sprite_name_dict():
    rval = {x:"player" for x in player_frames}
    rval |= {x:"ninja_girl" for x in range(0x8C0,0x8FF)}
    return rval

def load_grouped_dicts():

    # ATM manual lateral grouping of sprites (possibly already vertically grouped)
    # those are manual, but with the help of frame decode (sprite_decode.py) which analyzes
    # the whole set of game macro-objects
    mgsf = this_dir / "macro_grouped_sprites.json"
    with open(mgsf) as f:
        # load and convert to easily useable
        gd = json.load(f)
        dicts = [{int(k,16):[int(c,16) for c in v]
                        if isinstance(v,list) else [int(v,16)] for k,v in gd[x].items()}
                        for x in ["horizontal","vertical"]]

    # we need to check that values aren't found in keys as it would "loop" and hide sprite tiles
    for x in dicts:
        # collect keys
        keys = set(x)
        values = {e for v in x.values() for e in v}
        shared_values = values.intersection(keys)
        if shared_values:
            sh = [hex(x) for x in shared_values]
            raise Exception(f"in {mgsf}, values & key cross refs: {sh}")
    # also check that there aren't any shared keys between dicts
    shared_keys = set(dicts[0]) & set(dicts[1])
    if shared_keys:
        sh = [hex(x) for x in shared_keys]
        raise Exception(f"Shared keys between horiz/vert grouping dicts: {sh}")
    return dicts

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