from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib

from shared import *

sprite_names = dict()

with open(os.path.join(this_dir,"used_cluts.json")) as f:
    used_cluts = json.load(f)
    # set proper types
    used_cluts = {k:{int(k2):set(v2) for k2,v2 in v.items()} for k,v in used_cluts.items()}


dump_it = True
dump_dir = this_dir / "dumps"


if dump_it:
    if not os.path.exists(dump_dir):
        os.mkdir(dump_dir)
        with open(os.path.join(dump_dir,".gitignore"),"w") as f:
            f.write("*")


def ensure_empty(d):
    if os.path.exists(d):
        for f in os.listdir(d):
            os.remove(os.path.join(d,f))
    else:
        os.makedirs(d)

def dump_asm_bytes(*args,**kwargs):
    bitplanelib.dump_asm_bytes(*args,**kwargs)



def load_tileset(image_name,palette_index,side,tileset_name,dumpdir,dump=False,name_dict=None,cluts=None):

    if isinstance(image_name,str):
        full_image_path = os.path.join(this_dir,os.path.pardir,"sheets",image_name)
        tiles_1 = Image.open(full_image_path)
    else:
        tiles_1 = image_name
    nb_rows = tiles_1.size[1] // side
    nb_cols = tiles_1.size[0] // side


    tileset_1 = []

    if dump:
        dump_subdir = os.path.join(dumpdir,tileset_name)
        if palette_index == 0:
            ensure_empty(dump_subdir)

    tile_number = 0
    empty_list = []
    palette = set()

    for j in range(nb_rows):
        for i in range(nb_cols):

            if cluts and palette_index not in cluts.get(tile_number,empty_list):
                # no clut declared for that tile
                tileset_1.append(None)

            else:
                img = Image.new("RGB",(side,side))
                img.paste(tiles_1,(-i*side,-j*side))

                # only consider colors of used tiles
                palette.update(set(bitplanelib.palette_extract(img)))

                tileset_1.append(img)

                if dump:
                    img = ImageOps.scale(img,5,resample=Image.Resampling.NEAREST)
                    if name_dict:
                        name = name_dict.get(tile_number,"unknown")
                    else:
                        name = "unknown"

                    img.save(os.path.join(dump_subdir,f"{name}_{tile_number:02x}_{palette_index:02x}.png"))

            tile_number += 1

    return sorted(set(palette)),tileset_1


# ATM all colors are considered the same weight
# should rather 1) create a big pic with all sprites & all cluts
# 2) apply quantize on that image
def quantize_palette_16(rgb_tuples,img_type):
    rgb_configs = set(rgb_tuples)
    rgb_configs.remove(transparent)
    nb_quantize = 15
    # remove black, white, we don't want it quantized
    immutable_colors = (transparent,(0,0,0))
    for c in immutable_colors:
        rgb_configs.discard(c)



    dump_graphics = False
    # now compose an image with the colors
    clut_img = Image.new("RGB",(len(rgb_configs),1))
    for i,rgb in enumerate(rgb_configs):
        #rgb_value = (rgb[0]<<16)+(rgb[1]<<8)+rgb[2]
        clut_img.putpixel((i,0),rgb)

    reduced_colors_clut_img = clut_img.quantize(colors=nb_quantize,dither=0).convert('RGB')

    # get the reduced palette
    reduced_palette = [reduced_colors_clut_img.getpixel((i,0)) for i,_ in enumerate(rgb_configs)]
    # apply rounding now
    # reduced_palette = bitplanelib.palette_round(reduced_palette,0xF0)
    #print(len(set(reduced_palette))) # should still be 15
    # now create a dictionary by associating the original & reduced colors
    rval = dict(zip(rgb_configs,reduced_palette))

    # add black & white & transparent back
    for c in immutable_colors:
        rval[c] = c



    if True:  # debug it
        s = clut_img.size
        ns = (s[0]*30,s[1]*30)
        clut_img = clut_img.resize(ns,resample=0)
        clut_img.save(dump_dir / "{}_colors_not_quantized.png".format(img_type))
        reduced_colors_clut_img = reduced_colors_clut_img.resize(ns,resample=0)
        reduced_colors_clut_img.save(dump_dir / "{}_colors_quantized.png".format(img_type))

    # return it
    return rval


def paint_black(img,coords):
    for x,y in coords:
        img.putpixel((x,y),(0,0,0))

def change_color(img,color1,color2):
    rval = Image.new("RGB",img.size)
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            p = img.getpixel((x,y))
            if p==color1:
                p = color2
            rval.putpixel((x,y),p)
    return rval

def add_sprite(index,name,cluts=[0]):
    if isinstance(index,range):
        pass
    elif not isinstance(index,(list,tuple)):
        index = [index]
    for idx in index:
        sprite_names[idx] = name
        sprite_cluts[idx] = cluts

def add_hw_sprite(index,name,cluts=[0]):
    if isinstance(index,range):
        pass
    elif not isinstance(index,(list,tuple)):
        index = [index]
    for idx in index:
        sprite_names[idx] = name
        hw_sprite_cluts[idx] = cluts



nb_planes = 4
nb_colors = 1<<nb_planes


def apply_quantize(tile_set,quantized):
    if tile_set:
        for t in tile_set:
            if t:
                bitplanelib.replace_color_from_dict(t,quantized)

def remove_colors(imgname):
    img = Image.open(imgname)
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            c = img.getpixel((x,y))
            if c in colors_to_remove:
                img.putpixel((x,y),(0,0,0))
    return img

#sprite_sheet_dict = {i:remove_colors(os.path.join(sprites_path,f"sprites_pal_{i:02x}.png")) for i in range(16)}
tile_1_sheet_dict = {i:os.path.join(sheets_path,"tiles_24a000",f"pal_{i:02x}.png") for i in range(9)}
tile_0_sheet_dict = {i:os.path.join(sheets_path,"tiles_244000",f"pal_{i:02x}.png") for i in range(15)}

def load_contexted_tileset(tile_sheet_dict,context):
    tile_palette = set()
    tile_24a000_set_list = []

    for i in range(16):
        tsd = tile_1_sheet_dict.get(i)
        if tsd:
            tp,tile_set = load_tileset(tsd,i,16,pathlib.Path("tiles") / context,dump_dir,dump=dump_it,name_dict=None,cluts=used_cluts[context])
            tile_24a000_set_list.append(tile_set)
            tile_palette.update(tp)
        else:
            tile_24a000_set_list.append(None)

    if (0,0,0) not in tile_palette:
        tile_palette.add((0,0,0))
    bg_palette = sorted(tile_palette)

    lfp = len(bg_palette)
    if lfp>16:
        raise Exception(f"background: Too many colors {lfp} max 16")
    if lfp<16:
        bg_palette += [(0x10,0x20,0x30)]*(16-lfp)

    # pad just in case we don't have 16 colors (but we have)
    bg_palette += (nb_colors-len(bg_palette)) * [(0x10,0x20,0x30)]

    return tile_24a000_set_list,bg_palette

tile_24a000_set_list,bg_palette = load_contexted_tileset(tile_1_sheet_dict,"title_24a000")

tile_palette = set()
tile_244000_set_list = []

for i in range(16):
    tsd = tile_0_sheet_dict.get(i)
    if tsd:
        tp,tile_set = load_tileset(tsd,i,8,"tiles/244000/unquantized",dump_dir,dump=dump_it,name_dict=None,cluts=used_cluts["title_244000"])

        tile_244000_set_list.append(tile_set)
        tile_palette.update(tp)
    else:
        tile_244000_set_list.append(None)

fg_palette = sorted(tile_palette)

lfp = len(fg_palette)
if lfp>16:
    print(f"Foreground: Too many colors {lfp} max 16, quantizing")
    quantized = quantize_palette_16(fg_palette,"baddudes")


    for tile_set in tile_244000_set_list:
        apply_quantize(tile_set,quantized)


    # put transparent color first
    fg_palette = sorted(set(quantized.values()))

    if dump_it:
        dump_subdir = dump_dir / "tiles/244000/quantized"
        ensure_empty(dump_subdir)

        for palette_index,tile_set in enumerate(tile_244000_set_list):
            if tile_set:
                for tile_number,img in enumerate(tile_set):
                    if img:
                        img = ImageOps.scale(img,5,resample=Image.Resampling.NEAREST)
                        name = "unknown"

                        img.save(os.path.join(dump_subdir,f"{name}_{tile_number:02x}_{palette_index:02x}.png"))

fg_palette.remove(transparent)
fg_palette.insert(0,transparent)

if lfp<16:
    fg_palette += [(0x10,0x20,0x30)]*(16-lfp)



plane_orientations = [("standard",lambda x:x),
("flip",ImageOps.flip),
("mirror",ImageOps.mirror),
("flip_mirror",lambda x:ImageOps.flip(ImageOps.mirror(x)))]

def read_tileset(img_set_list,palette,plane_orientation_flags,cache,is_bob):
    next_cache_id = 1
    tile_table = []
    for n,img_set in enumerate(img_set_list):
        tile_entry = []
        if img_set:
            for i,tile in enumerate(img_set):
                entry = dict()
                if tile:

                    for b,(plane_name,plane_func) in zip(plane_orientation_flags,plane_orientations):
                        if b:

                            actual_nb_planes = nb_planes
                            wtile = plane_func(tile)

                            if is_bob:
                                y_start,wtile = bitplanelib.autocrop_y(wtile)
                                height = wtile.size[1]
                                actual_nb_planes += 1
                                bitplane_data = bitplanelib.palette_image2raw(wtile,None,palette,generate_mask=True,blit_pad=True,mask_color=transparent)
                            else:
                                height = 8
                                y_start = 0
                                bitplane_data = bitplanelib.palette_image2raw(wtile,None,palette,mask_color=transparent)

                            plane_size = len(bitplane_data) // actual_nb_planes
                            bitplane_plane_ids = []
                            for j in range(actual_nb_planes):
                                offset = j*plane_size
                                bitplane = bitplane_data[offset:offset+plane_size]

                                cache_id = cache.get(bitplane)
                                if cache_id is not None:
                                    bitplane_plane_ids.append(cache_id)
                                else:
                                    if any(bitplane):
                                        cache[bitplane] = next_cache_id
                                        bitplane_plane_ids.append(next_cache_id)
                                        next_cache_id += 1
                                    else:
                                        bitplane_plane_ids.append(0)  # blank
                            entry[plane_name] = {"height":height,"y_start":y_start,"bitplanes":bitplane_plane_ids}

                tile_entry.append(entry)

        tile_table.append(tile_entry)

    table_len = len(max(tile_table,key=len))

    new_tile_table = [[[] for _ in range(16)] for _ in range(table_len)]

    # reorder/transpose. We have 16 * 256 we need 256 * 16
    for i,u in enumerate(tile_table):
        for j,v in enumerate(u):
            new_tile_table[j][i] = v

    return new_tile_table


def dump_tiles(file_radix,palette,tile_table,tile_plane_cache):
    tiles_1_src = os.path.join(src_dir,file_radix+".68k")

    with open(tiles_1_src,"w") as f:
        f.write("palette:\n")
        palette_copy = palette.copy()
        # avoid that sometimes screen flashes purple when in fact it should be black
        if palette_copy[0] == transparent:
            palette_copy[0] = (0,0,0)
        bitplanelib.palette_dump(palette_copy,f,bitplanelib.PALETTE_FORMAT_ASMMOT)

        f.write("base:\n")
        for i,tile_entry in enumerate(tile_table):
            f.write("\tdc.l\t")
            if tile_entry:
                f.write(f"tile_{i:02x}-base")
            else:
                f.write("0")
            f.write("\n")

        for i,tile_entry in enumerate(tile_table):
            if tile_entry:
                tile_base = f"tile_{i:02x}"
                f.write(f"{tile_base}:\n")
                for j,t in enumerate(tile_entry):
                    f.write("\tdc.l\t")
                    if t:
                        f.write(f"tile_{i:02x}_{j:02x}-{tile_base}")
                    else:
                        f.write("0")
                    f.write("\n")


        for i,tile_entry in enumerate(tile_table):
            if tile_entry:
                for j,t in enumerate(tile_entry):
                    if t:
                        tile_base = f"tile_{i:02x}_{j:02x}"

                        f.write(f"{tile_base}:\n")
                        for orientation,_ in plane_orientations:
                            f.write("* {}\n".format(orientation))
                            if orientation in t:
                                data = t[orientation]
                                for bitplane_id in data["bitplanes"]:
                                    f.write("\tdc.l\t")
                                    if bitplane_id:
                                        f.write(f"tile_plane_{bitplane_id:02d}-{tile_base}")
                                    else:
                                        f.write("0")
                                    f.write("\n")
                                if len(t)==1:
                                    # optim: only standard
                                    break
                            else:
                                for _ in range(nb_planes):
                                    f.write("\tdc.l\t0\n")


                        #dump_asm_bytes(t["bitmap"],f)

        for k,v in tile_plane_cache.items():
            f.write(f"tile_plane_{v:02d}:")
            dump_asm_bytes(k,f)
    # now convert the asm file to full binary
    tiles_1_bin = os.path.join(data_dir,os.path.basename(os.path.splitext(tiles_1_src)[0])+".bin")
    asm2bin(tiles_1_src,tiles_1_bin)


tile_244000_cache = {}
tile_24a000_cache = {}

tile_24a000_table = read_tileset(tile_24a000_set_list,bg_palette,[True,False,False,False],cache=tile_24a000_cache, is_bob=False)
tile_244000_table = read_tileset(tile_244000_set_list,fg_palette,[True,False,False,False],cache=tile_244000_cache, is_bob=False)



dump_tiles("tiles_title_24a000",bg_palette,tile_24a000_table,tile_24a000_cache)
dump_tiles("tiles_title_244000",fg_palette,tile_244000_table,tile_244000_cache)


# high score tiles
tile_24a000_set_list,bg_palette = load_contexted_tileset(tile_1_sheet_dict,"highs_24a000")

tile_24a000_cache = {}

tile_24a000_table = read_tileset(tile_24a000_set_list,bg_palette,[True,False,False,False],cache=tile_24a000_cache, is_bob=False)

dump_tiles("tiles_highs_24a000",bg_palette,tile_24a000_table,tile_24a000_cache)

# start screen tiles
#tile_24a000_set_list,bg_palette = load_contexted_tileset(tile_1_sheet_dict,"game_start_24a000")

#tile_24a000_cache = {}

#tile_24a000_table = read_tileset(tile_24a000_set_list,bg_palette,[True,False,False,False],cache=tile_24a000_cache, is_bob=False)

#dump_tiles("tiles_game_start_24a000",bg_palette,tile_24a000_table,tile_24a000_cache)

