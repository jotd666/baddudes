from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess

this_dir = os.path.dirname(os.path.abspath(__file__))

data_dir = os.path.join(this_dir,"..","..","data")
src_dir = os.path.join(this_dir,"..","..","src","amiga")

sheets_path = os.path.join(this_dir,"..","sheets")

sprite_names = dict()


dump_it = False
dump_dir = os.path.join(this_dir,"dumps")


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
        if palette_index == 2:
            ensure_empty(dump_subdir)

    tile_number = 0
    palette = set()

    for j in range(nb_rows):
        for i in range(nb_cols):

            if cluts and palette_index not in cluts[tile_number]:
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




def remove_colors(imgname):
    img = Image.open(imgname)
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            c = img.getpixel((x,y))
            if c in colors_to_remove:
                img.putpixel((x,y),(0,0,0))
    return img

#sprite_sheet_dict = {i:remove_colors(os.path.join(sprites_path,f"sprites_pal_{i:02x}.png")) for i in range(16)}
tile_1_sheet_dict = {i:os.path.join(sheets_path,f"tiles_1_pal_{i:02x}.png") for i in [2,6,7]}

tile_palette = set()
tile_set_list = []

for i in range(16):
    tsd = tile_1_sheet_dict.get(i)
    if tsd:
        tp,tile_set = load_tileset(tsd,i,16,"tiles",dump_dir,dump=dump_it,name_dict=None)
        tile_set_list.append(tile_set)
        tile_palette.update(tp)
    else:
        tile_set_list.append(None)



full_palette = sorted(tile_palette)



# pad just in case we don't have 16 colors (but we have)
full_palette += (nb_colors-len(full_palette)) * [(0x10,0x20,0x30)]





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
                                bitplane_data = bitplanelib.palette_image2raw(wtile,None,palette,generate_mask=True,blit_pad=True)
                            else:
                                height = 8
                                y_start = 0
                                bitplane_data = bitplanelib.palette_image2raw(wtile,None,palette)

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

tile_plane_cache = {}
tile_table = read_tileset(tile_set_list,full_palette,[True,False,False,False],cache=tile_plane_cache, is_bob=False)


with open(os.path.join(src_dir,"palette.68k"),"w") as f:
    bitplanelib.palette_dump(full_palette,f,bitplanelib.PALETTE_FORMAT_ASMGNU)

tiles_1_src = os.path.join(src_dir,"tiles_1.68k")

with open(tiles_1_src,"w") as f:
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

subprocess.run(["vasmm68k_mot","-nosym","-Fbin",tiles_1_src,"-o",tiles_1_bin],check=True)

