from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib

from shared import *

sprite_names = dict()
palette_dict = dict()

def reformat_subdict(d):
    rval = {"cluts":set(d["cluts"])}
    attribs = d.get("attributes")
    if attribs:
        rval["attributes"] = attribs
    return rval

def reformat_dict(d):
    return {k:{int(k2):reformat_subdict(v2) for k2,v2 in v.items()} for k,v in d.items()}

with open(os.path.join(this_dir,"used_tile_cluts.json")) as f:
    # set proper types
    used_tile_cluts = reformat_dict(json.load(f))

with open(os.path.join(this_dir,"used_sprite_cluts.json")) as f:
    # set proper types
    used_sprite_cluts = reformat_dict(json.load(f))


dump_it = True
dump_dir = this_dir / "dumps"

src_gen_dir = src_dir / "generated"
if not src_gen_dir.exists():
    src_gen_dir.mkdir()

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

def process_multi_tiled_sprite(img,tiles_1,i,j,nb_cols,h,w,flipx):
    side = 16
    for hi in range(h):
        img.paste(tiles_1,(-i*side,-j*side))
##        i += 1
##        if i==nb_cols:
##            i=0
##            j+=1

# in that implementation, we have to provide a cluts dict as without it it would dump the whole set
# of tiles/sprites and it's pretty huge in games like BadDudes or other "big" games.
def load_tileset(image_name,palette_index,side,tileset_name,dumpdir,cluts,dump=False,name_dict=None):


    if isinstance(image_name,(str,pathlib.Path)):
        full_image_path = os.path.join(this_dir,os.path.pardir,"sheets",image_name)
        tiles_1 = Image.open(full_image_path)
    else:
        tiles_1 = image_name
    nb_rows = tiles_1.size[1] // side
    nb_cols = tiles_1.size[0] // side
    full_tileset = []
    # first, brutally read tileset from sheet so indices are linear
    for j in range(nb_rows):
        for i in range(nb_cols):
            img = Image.new("RGB",(side,side))
            img.paste(tiles_1,(-i*side,-j*side))
            full_tileset.append(img)

    tileset_1 = []

    if dump:
        dump_subdir = os.path.join(dumpdir,tileset_name)
        if palette_index == 0:
            ensure_empty(dump_subdir)

    # now we have an array of small images, way more convenient to work with
    # specially if the attributes make the sprite multi-tiled

    empty_list = {"cluts":[]}
    palette = set()

    for tile_number,tile_img in enumerate(full_tileset):
            cd = cluts.get(tile_number,empty_list)
            if palette_index not in cd["cluts"]:
                # no clut declared for that tile
                tileset_1.append(None)

            else:
                width = side
                height = side

                attributes = cd.get("attributes")
                if attributes:
                    data0 = attributes << 8
                    h = (1 << ((data0 & 0x1800) >> 11))
                    w = (1 << ((data0 & 0x0600) >>  9))
                    flipx = bool(data0 & 0x2000)
                    flipy = bool(data0 & 0x4000)
                    #print("attribs!!! ",tile_number,cd["cluts"],hex(attributes),h,w,flipx,flipy)

                    height *= h
                    width *= w

                img = Image.new("RGB",(width,height))
                if False: #attributes:
                    process_multi_tiled_sprite(img,tile_number,full_tileset,h,w,flipx)
                else:
                    # simple case
                    img.paste(tile_img)

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


    return sorted(set(palette)),tileset_1


# ATM all colors are considered the same weight
# should rather 1) create a big pic with all sprites & all cluts
# 2) apply quantize on that image
def quantize_palette(rgb_tuples,img_type,nb_quantize,transparent=None):
    rgb_configs = set(rgb_tuples)

    nb_target_colors = nb_quantize
    if transparent:
        rgb_configs.remove(transparent)
        # remove black, white, we don't want it quantized
        immutable_colors = (transparent,(0,0,0))
    else:
        immutable_colors = ((0,0,0),)

    for c in immutable_colors:
        rgb_configs.discard(c)
        nb_quantize -= 1

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

    result_nb = len(set(reduced_palette))
    if nb_quantize != result_nb:
        raise Exception(f"quantize: {img_type}: {nb_quantize} expected, found {result_nb}")
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
title_tile_24a000_sheet_dict = {i:sheets_path / "tiles_24a000" / "title" / f"pal_{i:02x}.png" for i in range(9)}
game_intro_tile_24a000_sheet_dict = {i:sheets_path / "tiles_24a000" / "game_intro" / f"pal_{i:02x}.png" for i in range(4)}
level_1_tile_24a000_sheet_dict = {i:sheets_path / "tiles_24a000" / "level_1" / f"pal_{i:02x}.png" for i in range(16)}
tile_0_sheet_dict = {i:sheets_path / "tiles_244000" / f"pal_{i:02x}.png" for i in range(15)}
sprite_sheet_dict = {i:sheets_path / "sprites" / f"pal_{i:02x}.png" for i in range(16)}

def load_contexted_tileset(tile_sheet_dict,context,nb_colors,is_bob,reuse_colors=set()):
    tile_palette = set()
    tile_24a000_set_list = []

    context_dir = pathlib.Path("sprites" if is_bob else "tiles") / context
    used_cluts_dict = used_sprite_cluts if is_bob else used_tile_cluts

    for i in range(16):
        tsd = tile_sheet_dict.get(i)
        if tsd:
            tp,tile_set = load_tileset(tsd,i,16,context_dir,dump_dir,dump=dump_it,cluts=used_cluts_dict[context])
            tile_24a000_set_list.append(tile_set)
            tile_palette.update(tp)
        else:
            tile_24a000_set_list.append(None)

    if (0,0,0) not in tile_palette:
        tile_palette.add((0,0,0))

    # subtract the colors contained in "reuse_colors"
    bg_palette = sorted(tile_palette - reuse_colors)

    lfp = len(bg_palette)
    if lfp==1:
        raise Exception(f"{context}: no colors found, empty tiles?")
    if lfp>nb_colors:
        print(f"{context}: Too many colors {lfp} max {nb_colors}, quantizing")

        quantized = quantize_palette(bg_palette,context,nb_colors)


        for tile_set in tile_24a000_set_list:
            apply_quantize(tile_set,quantized)


        # put transparent color first, re-inject reused colors
        bg_palette = sorted(set(quantized.values()) | reuse_colors)

##        if dump_it:
##            dump_subdir = dump_dir / "tiles/244000/quantized"
##            ensure_empty(dump_subdir)
##
##            for palette_index,tile_set in enumerate(tile_244000_set_list):
##                if tile_set:
##                    for tile_number,img in enumerate(tile_set):
##                        if img:
##                            img = ImageOps.scale(img,5,resample=Image.Resampling.NEAREST)
##                            name = "unknown"
##
##                            img.save(os.path.join(dump_subdir,f"{name}_{tile_number:02x}_{palette_index:02x}.png"))
    if lfp<nb_colors:
        bg_palette += [(0x10,0x20,0x30)]*(nb_colors-lfp)

    return tile_24a000_set_list,bg_palette




plane_orientations = [("standard",lambda x:x),
("mirror",ImageOps.mirror),
#("flip",ImageOps.flip),
#("flip_mirror",lambda x:ImageOps.flip(ImageOps.mirror(x)))
]

def get_nb_planes(palette):
    import math
    nb_planes = int(math.log2(len(palette)))
    return nb_planes

def read_tileset(img_set_list,palette,cache,is_bob,generate_mask):
    next_cache_id = 1
    tile_table = []
    plane_orientation_flags = [True,is_bob]

    nb_planes = get_nb_planes(palette)
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
                                generate_mask = bitplanelib.MASK_ON
                            else:
                                y_start = 0
                                if generate_mask:
                                    # for tiles that perform CPU-cookie cut, saves the NOT operation
                                    generate_mask = bitplanelib.MASK_INVERTED

                            height = wtile.size[1]
                            width = (wtile.size[0]//16)+2
                            if width % 2:
                                width += 1   # not sure it will solve anything, rather make it differenly trashed...
                            bitplane_data = bitplanelib.palette_image2raw(wtile,None,palette,generate_mask=generate_mask,blit_pad=is_bob,mask_color=transparent)
                            if generate_mask:
                                actual_nb_planes += 1
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
                            entry[plane_name] = {"height":height,"width":width,"y_start":y_start,"bitplanes":bitplane_plane_ids}

                tile_entry.append(entry)

        tile_table.append(tile_entry)

    table_len = len(max(tile_table,key=len))

    new_tile_table = [[{} for _ in range(16)] for _ in range(table_len)]

    # reorder/transpose. We have 16 * 256 we need 256 * 16
    for i,u in enumerate(tile_table):
        for j,v in enumerate(u):
            new_tile_table[j][i] = v

    return new_tile_table


def dump_tiles(file_radix,palette,tile_table,tile_plane_cache,add_dimension_info=False):
    nb_planes = get_nb_planes(palette)

    tiles_1_src = src_gen_dir / f"{file_radix}.68k"

    with open(tiles_1_src,"w") as f:
        f.write(f"\tdc.w\t{nb_planes}   ; nb planes \n")
        f.write("palette:\n")
        palette_copy = palette.copy()
        # avoid that sometimes screen flashes purple when in fact it should be black
        if palette_copy[0] == transparent:
            palette_copy[0] = (0,0,0)
        bitplanelib.palette_dump(palette_copy,f,bitplanelib.PALETTE_FORMAT_ASMMOT)

        f.write("base:\n")
        for i,tile_entry in enumerate(tile_table):
            f.write("\tdc.l\t")

            if any(tile_entry):
                f.write(f"tile_{i:02x}-base")
            else:
                f.write("0")
            f.write(f"\t; ${i:04x}\n")

        for i,tile_entry in enumerate(tile_table):
            if any(tile_entry):
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
                            f.write("* <{}>\n".format(orientation))
                            if orientation in t:
                                data = t[orientation]
                                if add_dimension_info:
                                    # find h,w,yoffset
                                    f.write("\tdc.w\t{height},{width},{y_start}  ; h,w,y offset\n".format(**data))
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

def process_tile_context(context_name,tile_sheet_dict,nb_colors,is_bob=False,use_palette_colors=None):

    # use previous colors (tiles) to maximize the chance of not quantizing colors
    reuse_colors = palette_dict[use_palette_colors] if use_palette_colors else []

    tile_24a000_set_list,bg_palette = load_contexted_tileset(tile_sheet_dict,context_name,nb_colors,is_bob) #,reuse_colors=set(reuse_colors))
    tile_24a000_cache = {}

    if reuse_colors:
        # temp: just fill with as many dummy colors as in reuse_colors
        bg_palette = [(0x10,0x20,0x30)]*len(reuse_colors) + bg_palette

    tile_24a000_table = read_tileset(tile_24a000_set_list,bg_palette,cache=tile_24a000_cache, is_bob=is_bob, generate_mask=is_bob)
    prefix = "sprites_" if is_bob else "tiles_"

    dump_tiles(prefix+context_name,bg_palette,tile_24a000_table,tile_24a000_cache,add_dimension_info=is_bob)

    palette_dict[context_name] = bg_palette

tile_palette = set()
tile_244000_set_list = []

# hack replace a close color by another, so we get 8 colors / possibly 3 planes
to_replace = (0, 0, 104)
replace_by = (0, 0, 123)

for i in range(16):
    tsd = tile_0_sheet_dict.get(i)
    if tsd:
        tp,tile_set = load_tileset(tsd,i,8,"tiles/244000",dump_dir,dump=dump_it,cluts=used_tile_cluts["title_244000"])
        for tile in tile_set:
            if tile:
                bitplanelib.replace_color(tile,{to_replace},replace_by)

        tile_244000_set_list.append(tile_set)
        tile_palette.update(tp)
    else:
        tile_244000_set_list.append(None)

tile_palette.discard(to_replace)
fg_palette = sorted(tile_palette)

lfp = len(fg_palette)

if lfp>8:
    raise Exception(f"Foreground: Too many colors {lfp} max 8")


fg_palette.remove(transparent)
fg_palette.insert(0,transparent)

if lfp<8:
    fg_palette += [(0x10,0x20,0x30)]*(8-lfp)


# tiles

if False:
    tile_244000_cache = {}
    fg_palette = [(0x10,0x20,0x30)]*56 + fg_palette

    tile_244000_table = read_tileset(tile_244000_set_list,fg_palette,
    cache=tile_244000_cache,
    generate_mask = True,
    is_bob=False)


    dump_tiles("tiles_title_244000",fg_palette,tile_244000_table,tile_244000_cache)

    process_tile_context("title_24a000",title_tile_24a000_sheet_dict,16)
    process_tile_context("game_intro_24a000",game_intro_tile_24a000_sheet_dict,32)
    process_tile_context("highs_24a000",title_tile_24a000_sheet_dict,16)
    process_tile_context("level_1_24a000",level_1_tile_24a000_sheet_dict,32)

# sprites
    process_tile_context("title_24a000",title_tile_24a000_sheet_dict,16)
else:
    process_tile_context("game_intro_24a000",game_intro_tile_24a000_sheet_dict,32)
    process_tile_context("level_1_24a000",level_1_tile_24a000_sheet_dict,32)

# game intro. Not gaining any colors by passing the associated screen tile colors...
process_tile_context("game_intro",sprite_sheet_dict,32,is_bob=True,use_palette_colors="game_intro_24a000")

process_tile_context("game_level_1",sprite_sheet_dict,32,is_bob=True,use_palette_colors="level_1_24a000")

