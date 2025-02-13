from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib,shutil

from shared import *

import convert_dudes_pics
import convert_truck_pics
import convert_front_objects

import extract_used_tiles
import extract_used_sprites

extract_used_tiles.doit()
extract_used_sprites.doit()
convert_dudes_pics.doit()

sprite_names = dict()
palette_dict = dict()

# blue ninja tiles are pre-mirrored as there are a lot of them
# at the same time
pre_mirrored_sprites = {k:{2} for k in range(0x200,0x348)}

side_grouped_dict,vert_grouped_dict = load_grouped_dicts()

def reformat_subdict(d):
    rval = {"cluts":set(d["cluts"])}
    attribs = d.get("attributes")
    if attribs:
        rval["attributes"] = attribs
    return rval

def reformat_dict(d):
    return {k:{int(k2):reformat_subdict(v2) for k2,v2 in v.items()} for k,v in d.items()}

with open(used_tile_cluts_file) as f:
    # set proper types
    used_tile_cluts = reformat_dict(json.load(f))

with open(used_sprite_cluts_file) as f:
    # set proper types
    used_sprite_cluts = reformat_dict(json.load(f))


dump_it = True


if not generated_src_dir.exists():
    generated_src_dir.mkdir()

if dump_it:
    if os.path.exists(dump_dir):
        try:
            shutil.rmtree(dump_dir)
        except OSError:
            print(f"Warning: cannot cleanup, locked subdir in {dump_dir}?")

    if not os.path.exists(dump_dir):
        os.mkdir(dump_dir)
        with open(os.path.join(dump_dir,".gitignore"),"w") as f:
            f.write("*")




def dump_asm_bytes(*args,**kwargs):
    bitplanelib.dump_asm_bytes(*args,**kwargs)

def process_single_tiled_sprite(tile_number,full_tileset,height,width):
    side_group = side_grouped_dict.get(tile_number)
    if side_group:
        group_tiles = [tile_number]+side_group
        img = Image.new("RGB",(width*len(group_tiles),height))
        # rebuild bigger pic from unique tile columns
        for i,gtn in enumerate(group_tiles):
            img_part = process_sprite(gtn,full_tileset,height,width)
            img.paste(img_part,(width*i,0))

    else:
        img = process_sprite(tile_number,full_tileset,height,width)
    return img

def process_sprite(tile_number,full_tileset,height,width):
    img = Image.new("RGB",(width,height))
    # simple case when there are 2 different sizes used for that sprite
    img.paste(full_tileset[tile_number])
    return img


def process_multi_tiled_sprite(tile_number,full_tileset,h,w,height,width):
    side_group = side_grouped_dict.get(tile_number)
    if side_group:
        # sprite has a manually set lateral/side tile grouping
        # allows to save 1 blit and 25% chip bandwidth on sprites that are only used together (wheel parts, body parts)
        # also saves a lot of memory

        group_tiles = [tile_number]+side_group
        img = Image.new("RGB",(width*len(group_tiles),height))

        # rebuild bigger pic from unique tile columns
        for i,gtn in enumerate(group_tiles):
            img_part = process_multi_tiled_sprite_single_column(gtn,full_tileset,h,w,height,width)
            img.paste(img_part,(width*i,0))
    else:
        vert_group = vert_grouped_dict.get(tile_number)
        if vert_group:
            # sprite has a manually set vertical tile grouping
            # allows to save 1 blit and 25% chip bandwidth on sprites that are only used together (wheel parts, body parts)
            # also saves a lot of memory
            group_tiles = [tile_number]+vert_group
            img = Image.new("RGB",(width,height*len(group_tiles)))
            # rebuild bigger pic from unique tile columns
            for i,gtn in enumerate(group_tiles):
                img_part = process_multi_tiled_sprite_single_column(gtn,full_tileset,h,w,height,width)
                img.paste(img_part,(0,height*i))
        else:
            # not grouped, normal column grouping
            img = process_multi_tiled_sprite_single_column(tile_number,full_tileset,h,w,height,width)
    return img

def process_multi_tiled_sprite_single_column(tile_number,full_tileset,h,w,height,width):
    side = 16
    x_start = 0
    y_start = 0

    img = Image.new("RGB",(width,height))
    # quick hack because either wrong log or something else but fuck it
    # there aren't any sprites with h>4, this fixes Karnov sprites
    if h>4:
        h = 4


    if h>1:
        for hi in range(h):
            img.paste(full_tileset[tile_number],(side*x_start,side*y_start))
            tile_number += 1
            y_start += 1
    if w>1:
        # doesn't happen in this game, we'll use side-grouping manually
        for hi in range(w):
            img.paste(full_tileset[tile_number],(side*x_start,side*y_start))
            tile_number += 1
            x_start += 1

    return img

# in that implementation, we have to provide a cluts dict as without it it would dump the whole set
# of tiles/sprites and it's pretty huge in games like BadDudes or other "big" games.
def load_tileset(image_name,palette_index,side,tileset_name,cluts,name_dict=None,postload_callback=None,is_bob=False):
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

    tileset_1 = [None]*(len(full_tileset)*2)  # take multi-size into account 0-FFF: simple, higher: multiple

    if dump_it:
        dump_subdir = dump_dir / tileset_name
        ensure_exists(dump_subdir)

    # now we have an array of small images, way more convenient to work with
    # specially if the attributes make the sprite multi-tiled

    empty_list = {"cluts":[]}
    palette = set()

    for tile_number,tile_img in enumerate(full_tileset):
        cd = cluts.get(tile_number,empty_list)
        if palette_index not in cd["cluts"]:
            # no clut declared for that tile
            pass

        else:
            # found an entry, but is there a relevant entry with multi-tile? (some rare cases)
            cdm = cluts.get(tile_number+0x1000,empty_list)
            dual = False
            if palette_index in cdm["cluts"]:
                # clut declared for that tile: we have a dual sprite
                cd = cdm
                dual = True


            width = side
            height = side

            attributes = cd.get("attributes")
            if attributes:
                data0 = attributes << 8
                h = (1 << ((data0 & 0x1800) >> 11))
                w = (1 << ((data0 & 0x0600) >>  9))
                flipx = bool(data0 & 0x2000)
                # ignoring flipy, we can do that dynamically with blitter
                #print("attribs!!! ",tile_number,cd["cluts"],hex(attributes),h,w,flipx,flipy)

                height *= h
                width *= w

            multi = False

            if attributes and (h!=1 or w!=1):
                img = process_multi_tiled_sprite(tile_number,full_tileset,h,w,height,width)
                tileset_1[tile_number+0x1000] = img   # add the multi-sprite with a shifted position
                multi = True
            else:
                # simple case
                if is_bob:
                    tileset_1[tile_number] = process_single_tiled_sprite(tile_number,full_tileset,side,side)
                else:
                    # simple tile, not a bob, we don't want grouping!!
                    tileset_1[tile_number] = process_sprite(tile_number,full_tileset,side,side)
            if dual:
                # repeat for simple (only for bobs)
                tileset_1[tile_number] = process_single_tiled_sprite(tile_number,full_tileset,side,side)


            if dump_it:
                source = tileset_1[tile_number+0x1000 if multi else tile_number]
                img = ImageOps.scale(source,5,resample=Image.Resampling.NEAREST)
                if name_dict:
                    name = name_dict.get(tile_number,"unknown")
                else:
                    name = "unknown"
                iname = f"{name}_{tile_number:03x}_{palette_index:02x}"
                bname = iname
                if multi:
                    iname += "_multi"
                img.save(os.path.join(dump_subdir,f"{iname}.png"))
                if dual:
                    # also dump the normal image
                    source = tileset_1[tile_number]
                    img = ImageOps.scale(source,5,resample=Image.Resampling.NEAREST)
                    if name_dict:
                        name = name_dict.get(tile_number,"unknown")
                    else:
                        name = "unknown"
                    img.save(os.path.join(dump_subdir,f"{bname}_simple.png"))


    if postload_callback:
        postload_callback(tileset_1,palette_index)

    # now that callback has been called, compose palette (so it can remove unwanted tiles
    # and consider color changes/removals
    for img in tileset_1:
        if img:
            # only consider colors of used tiles
            palette.update(set(bitplanelib.palette_extract(img)))

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



    if dump_it:  # debug it, create 2 rows, 1 non-quantized, and 1 quantized, separated by bloack
        s = clut_img.size
        ns = (s[0]*30,s[1]*30)
        clut_img = clut_img.resize(ns,resample=0)
        whole_image = Image.new("RGB",(clut_img.size[0],clut_img.size[1]*3))
        whole_image.paste(clut_img,(0,0))
        reduced_colors_clut_img = reduced_colors_clut_img.resize(ns,resample=0)
        whole_image.paste(reduced_colors_clut_img,(0,clut_img.size[1]*2))
        whole_image.save(dump_dir / "{}_colors.png".format(img_type))

    result_nb = len(set(reduced_palette))
    if nb_quantize < result_nb:
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
level_2_tile_24a000_sheet_dict = {i:sheets_path / "tiles_24a000" / "level_2" / f"pal_{i:02x}.png" for i in range(8,16)}
level_3_tile_24a000_sheet_dict = {i:sheets_path / "tiles_24a000" / "level_3" / f"pal_{i:02x}.png" for i in range(13,16)}
level_3_tile_24d000_sheet_dict = {i:sheets_path / "tiles_24d000" / "level_3" / f"pal_{i:02x}.png" for i in range(9)}
level_4_tile_24a000_sheet_dict = {i:sheets_path / "tiles_24a000" / "level_4" / f"pal_{i:02x}.png" for i in range(0,16)}
level_5_tile_24a000_sheet_dict = {i:sheets_path / "tiles_24a000" / "level_5" / f"pal_{i:02x}.png" for i in range(0,16)}
level_6_tile_24a000_sheet_dict = {i:sheets_path / "tiles_24a000" / "level_6" / f"pal_{i:02x}.png" for i in range(0,16)}
level_7_tile_24a000_sheet_dict = {i:sheets_path / "tiles_24a000" / "level_7" / f"pal_{i:02x}.png" for i in range(0,16)}
tile_0_sheet_dict = {i:sheets_path / "tiles_244000" / f"pal_{i:02x}.png" for i in range(15)}
sprite_sheet_dict = {i:sheets_path / "sprites" / f"pal_{i:02x}.png" for i in range(16)}

def load_contexted_tileset(tile_sheet_dict,context,nb_colors,is_bob):
    tile_palette = set()
    tile_24a000_set_list = []

    context_dir = pathlib.Path("sprites" if is_bob else "tiles") / context
    used_cluts_dict = used_sprite_cluts if is_bob else used_tile_cluts

    for i in range(16):
        tsd = tile_sheet_dict.get(i)
        if tsd:
            tp,tile_set = load_tileset(tsd,i,16,context_dir,cluts=used_cluts_dict[context],is_bob=is_bob)
            tile_24a000_set_list.append(tile_set)
            tile_palette.update(tp)
        else:
            tile_24a000_set_list.append(None)

    if (0,0,0) not in tile_palette:
        tile_palette.add((0,0,0))

    # convert to rgb4
    # subtract the colors contained in "reuse_colors"
    tile_palette.discard(transparent)
    # demote to rgb4 to avoid quantization
    # tile_palette = {bitplanelib.rgb4_to_rgb_triplet(bitplanelib.to_rgb4_color(x)) for x in tile_palette}
    bg_palette = sorted(tile_palette)

    lfp = len(bg_palette)
    if lfp==1:
        raise Exception(f"{context}: no colors found, empty tiles?")
    if lfp>nb_colors:
        print(f"{context}: Too many colors {lfp} max {nb_colors}, quantizing")

        nb_colors_to_try = nb_colors
        prev_quantized = None
        while True:
            # quantize requires several passes to optimize number of colors
            quantized = quantize_palette(bg_palette,context,nb_colors_to_try)

            qc = set(quantized.values())
            if len(qc) < nb_colors:
                print(f"retry: {len(qc)} < {nb_colors}, try with {nb_colors_to_try}")
                nb_colors_to_try += 1
                prev_quantized = quantized
            else:
                break

        if len(qc) > nb_colors:
            # last quantize overshoot: revert to previous
            print("quantize overshoot, backtracking")
            quantized = prev_quantized
            qc = set(quantized.values())

        lfp = len(qc)       # update nb colors


        for tile_set in tile_24a000_set_list:
            apply_quantize(tile_set,quantized)


        # put transparent color first, re-inject reused colors
        bg_palette = sorted(qc)

        if dump_it:
            dump_subdir = dump_dir / context_dir / "quantized"
            ensure_exists(dump_subdir)


            for palette_index,tile_set in enumerate(tile_24a000_set_list):
                if tile_set:
                    for tile_number,img in enumerate(tile_set):
                        if img:
                            img = ImageOps.scale(img,5,resample=Image.Resampling.NEAREST)
                            name = "unknown"

                            img.save(os.path.join(dump_subdir,f"{name}_{tile_number:02x}_{palette_index:02x}.png"))
    if lfp<nb_colors:
        bg_palette += [(0x30,0x40,0x50)]*(nb_colors-lfp)

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
                            if plane_name == "mirror":
                                # check if we must pre-generate mirror plane
                                pms_clut = pre_mirrored_sprites.get(i)
                                if pms_clut and n in pms_clut:
                                    pass
                                else:
                                    # don't pre-compute mirror unless explicitly set
                                    entry[plane_name] = None
                                    continue

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
                            width = (wtile.size[0]//8)+2
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


def dump_tiles(file_radix,palette,tile_table,tile_plane_cache,add_dimension_info=False,palette_shift=0):
    nb_planes = get_nb_planes(palette)

    tiles_1_src = generated_src_dir / f"{file_radix}.68k"

    nb_planes_blocks = len(tile_plane_cache)
    with open(tiles_1_src,"w") as f:
        f.write(f"\tdc.w\t{nb_planes}   ; nb planes \n")
        f.write(f"\tdc.w\t{palette_shift}   ; nb shifted colors \n")
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
                f.write(f"tile_{i:03x}-base")
            else:
                f.write("0")
            f.write(f"\t; ${i:04x}\n")

        for i,tile_entry in enumerate(tile_table):
            if any(tile_entry):
                tile_base = f"tile_{i:03x}"
                f.write(f"{tile_base}:\n")
                for j,t in enumerate(tile_entry):
                    f.write("\tdc.l\t")
                    if t:
                        f.write(f"tile_{i:03x}_{j:02x}-{tile_base}")
                    else:
                        f.write("0")
                    f.write("\n")


        for i,tile_entry in enumerate(tile_table):
            if tile_entry:
                for j,t in enumerate(tile_entry):
                    if t:
                        tile_base = f"tile_{i:03x}_{j:02x}"

                        f.write(f"{tile_base}:\n")
                        for orientation,_ in plane_orientations:
                            f.write("* <{}>\n".format(orientation))
                            if orientation in t:

                                data = t[orientation]
                                if data:
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
                                    # no data:
                                    # don't pre-compute mirror unless explicitly set
                                    f.write("\tdc.w\t0   | no pre-computed mirror\n")


                            else:
                                for _ in range(nb_planes):
                                    f.write("\tdc.l\t0\n")


                        #dump_asm_bytes(t["bitmap"],f)

        for k,v in tile_plane_cache.items():
            f.write(f"\tdc.w\t0   ; plane {v:02d} orientation\n")
            f.write(f"tile_plane_{v:02d}:\n")
            dump_asm_bytes(k,f)
    # now convert the asm file to full binary
    tiles_1_bin = os.path.join(data_dir,os.path.basename(os.path.splitext(tiles_1_src)[0])+".bin")
    asm2bin(tiles_1_src,tiles_1_bin)

def process_tile_context(context_name,tile_sheet_dict,nb_colors,is_bob=False,shift_palette_count=0,first_pass=False,first_colors=None):


    tile_24a000_set_list,bg_palette = load_contexted_tileset(tile_sheet_dict,context_name,nb_colors,is_bob)
    tile_24a000_cache = {}

    if shift_palette_count:
        # temp: just fill with as many dummy colors as in reuse_colors
        bg_palette = [(0x10,0x20,0x30)]*shift_palette_count + bg_palette

    elif first_colors:
        # imposed first colors, that HAVE to be in the palette
        # bg_palette contains all colors, and need reordering
        first_colors_set = set(first_colors)
        bg_palette_no_first_colors = [x for x in bg_palette if x not in first_colors_set]
        # same colors, but reordered according to first colors constraint, allows to blit unrelated objects
        # to that layer with less bitplanes so faster/less data to store
        bg_palette = first_colors + bg_palette_no_first_colors

        if len(bg_palette)<nb_colors:
            # pad
            bg_palette += [(0x10,0x20,0x30)]*(nb_colors-len(bg_palette))


    if first_pass:
        # pass only done to extract palette, no need to generate a file
        pass
    else:
        tile_24a000_table = read_tileset(tile_24a000_set_list,bg_palette,cache=tile_24a000_cache, is_bob=is_bob, generate_mask=is_bob)
        prefix = "sprites_" if is_bob else "tiles_"

        dump_tiles(prefix+context_name,bg_palette,tile_24a000_table,tile_24a000_cache,add_dimension_info=is_bob,palette_shift=shift_palette_count)

    palette_dict[context_name] = bg_palette


def process_8x8_tile_layer(context,max_colors,colors_last,postload_callback=None):
    tile_palette = set()
    tile_244000_set_list = []

    # hack replace a close color by another, so we get 8 colors / possibly 3 planes
    to_replace = (0, 0, 104)
    replace_by = (0, 0, 123)

    for i in range(16):
        tsd = tile_0_sheet_dict.get(i)
        if tsd:
            tp,tile_set = load_tileset(tsd,i,8,"tiles/"+context,cluts=used_tile_cluts[context],postload_callback=postload_callback)
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

    if lfp>max_colors:
        print(fg_palette)
        raise Exception(f"Foreground {context}: Too many colors {lfp} max {max_colors}")

    transparent_first(fg_palette,transparent)

    if lfp<max_colors:
        fg_palette += [(0x10,0x20,0x30)]*(max_colors-lfp)

    tile_244000_cache = {}
    if colors_last:
        # pad so colors are last (not very useful for sprites, though)
        fg_palette = [(0x10,0x20,0x30)]*(64-max_colors) + fg_palette

    tile_244000_table = read_tileset(tile_244000_set_list,fg_palette,
    cache=tile_244000_cache,
    generate_mask = True,
    is_bob=False)
    dump_tiles("tiles_"+context,fg_palette,tile_244000_table,tile_244000_cache)

# tiles

def postprocess_game_osd_tiles(tileset,palette_index):
    old_len = len(tileset)
    if palette_index == 1:
        # remove all yellow digits we'll go dynamic on those
        tileset[:] = [None]*old_len
    else:
        # just kill all high tiles
        tileset[0x80:] = [None]*(old_len-0x80)

        # the "life" tile colors should be changed temporarily. We're changing
        # light pink by green and pink by white, which makes 4 colors for all sprites
        if palette_index==0:
            cyan_from_time = (0, 230, 176)
            pinks = ((230, 142, 159), (230, 176, 176),  # from "life" head
            (176,34,142),(230,56,208))                   # from health dots

            # we have to sacrifice the 2 nuances of pink in health dots because "1-LIFE"
            # text needs white and sprites can only use 3 colors
            color_rep = {pinks[0]:(230, 230, 230),pinks[1]:cyan_from_time,
            pinks[2]:cyan_from_time,pinks[3]:cyan_from_time}
            for life_tile in [0x6D,0x6F,0x72]:
                bitplanelib.replace_color_from_dict(tileset[life_tile],color_rep)

generate_for_levels = [False]*8

#generate_for_levels[1] = True
#generate_for_levels[2] = True
#generate_for_levels[3] = True
#generate_for_levels[4] = True
generate_for_levels[6] = True
# set to "False" for faster operation when working on game sprite/tiles
if generate_for_levels[0]:  # title/intro é game fonts

    process_8x8_tile_layer("title_244000",colors_last=True,max_colors=8)
    process_8x8_tile_layer("game_intro_244000",colors_last=True,max_colors=8)
    process_8x8_tile_layer("game_244000",colors_last=False,max_colors=4,postload_callback=postprocess_game_osd_tiles)

    process_tile_context("title_24a000",title_tile_24a000_sheet_dict,16)
    process_tile_context("game_intro_24a000",game_intro_tile_24a000_sheet_dict,32)
    process_tile_context("highs_24a000",title_tile_24a000_sheet_dict,16)

if generate_for_levels[1]:
    truck_nb_planes = 3
    process_tile_context("level_1_24a000",level_1_tile_24a000_sheet_dict,32,first_pass=True)
    truck_used_colors = convert_truck_pics.doit_truck_1(palette_dict["level_1_24a000"],truck_nb_planes)
    process_tile_context("level_1_24a000",level_1_tile_24a000_sheet_dict,32,first_pass=False,first_colors=truck_used_colors)
    convert_front_objects.doit_level_1()
    process_tile_context("game_level_1",sprite_sheet_dict,32,is_bob=True,shift_palette_count=32)

if generate_for_levels[2]:
    truck_nb_planes = 3
    nb_truck_colors = 1<<truck_nb_planes
    nb_tiles_colors = 8
    process_tile_context("level_2_24a000",level_2_tile_24a000_sheet_dict,nb_tiles_colors,first_pass=True)
    truck_used_colors = convert_truck_pics.doit_truck_2(palette_dict["level_2_24a000"],truck_nb_planes)
    process_tile_context("level_2_24a000",level_2_tile_24a000_sheet_dict,nb_tiles_colors,first_pass=False,first_colors=truck_used_colors)
    process_tile_context("game_level_2",sprite_sheet_dict,64-nb_tiles_colors,is_bob=True,shift_palette_count=nb_tiles_colors)
    convert_front_objects.doit_level_2()

if generate_for_levels[3]:
    process_tile_context("level_3_24d000",level_3_tile_24d000_sheet_dict,16,first_pass=False)
    process_tile_context("level_3_24a000",level_3_tile_24a000_sheet_dict,16,first_pass=False)
    process_tile_context("game_level_3",sprite_sheet_dict,48,is_bob=True,shift_palette_count=16)
if generate_for_levels[4]:
    process_tile_context("level_4_24a000",level_4_tile_24a000_sheet_dict,32,first_pass=False)
    process_tile_context("game_level_4",sprite_sheet_dict,32,is_bob=True,shift_palette_count=32)
if generate_for_levels[5]:
    process_tile_context("level_5_24a000",level_5_tile_24a000_sheet_dict,16,first_pass=False)
    process_tile_context("game_level_5",sprite_sheet_dict,48,is_bob=True,shift_palette_count=16)

if generate_for_levels[6]:
    process_tile_context("level_6_24a000",level_6_tile_24a000_sheet_dict,16,first_pass=False)
    process_tile_context("game_level_6",sprite_sheet_dict,48,is_bob=True,shift_palette_count=16)

if generate_for_levels[7]:
    process_tile_context("level_7_24a000",level_7_tile_24a000_sheet_dict,16,first_pass=False)
    process_tile_context("game_level_7",sprite_sheet_dict,48,is_bob=True,shift_palette_count=16)

