import json,os,collections,pathlib

this_dir = pathlib.Path(__file__).absolute().parent
used_dict = {}
dropped_tile_index = set()

used_cluts_file = this_dir / "used_tile_cluts.json"
used_graphics_dir = this_dir / "used_graphics"

def new_used_tiles():
    return collections.defaultdict(lambda : collections.defaultdict(list))

def add_digits_and_letters(n):
    for i in range(ord("A"),ord("Z")+1):
        used_dict[n][i]["cluts"].append(0)
    for i in range(ord("0"),ord("9")+1):
        used_dict[n][i]["cluts"].append(0)


# get dude tiles (big dude pics in intro) and don't consider their tiles
for i in range(2):
    with open(used_graphics_dir / f"dudes_{i}_tiles","rb") as f:
        f.seek(0x380)       # consider first tiles as used
        contents = f.read()
        for j in range(0,len(contents),2):
            tile_index = ((contents[j]<<8)+contents[j+1])&0xFFF
            if tile_index > 0x100:
                dropped_tile_index.add(tile_index)


##if os.path.exists(used_cluts_file):
##    with open(used_cluts_file) as f:
##        used_dict = json.load(f)

tiles_dir = used_graphics_dir / "tiles"
for n in os.listdir(tiles_dir):
    tiles_file = tiles_dir / n

    with open(tiles_file,"rb") as f:
        contents = f.read()

    used_tiles = new_used_tiles()

    tile_index = 0
    for offset in range(0,len(contents),16):
        is_244000 = n == "title_244000"
        if tile_index and (not is_244000 or tile_index not in dropped_tile_index):
            block = contents[offset:offset+16]
            for i,c in enumerate(block):
                if c:
                    if i==3 and is_244000:
                        # drop the yellow tiles in title, only useful to make title
                        # flash but renders ugly and eats a lot of colors for nothing
                        pass
                    else:
                        if n == "level_3_24a000" and tile_index < 0x100:
                            # we can't rely on that info, the game writes stuff but
                            # it has no visible effect. Only used tiles are 0x100->0x110 (water)
                            pass
                        else:
                            used_tiles[tile_index]["cluts"].append(i)
        tile_index += 1

    used_dict[n] = used_tiles

# force use of clut 0 for all letters & numbers in tileset 244000

add_digits_and_letters("title_244000")

# small font pack for game intro
n = "game_intro_244000"
used_dict[n] = new_used_tiles()
for i in range(ord("A"),ord("Z")+1):
    used_dict[n][i]["cluts"].append(0)
used_dict[n][ord("?")]["cluts"].append(0)

n = "game_244000"
#used_dict[n] = new_used_tiles()
add_digits_and_letters(n)
for i in range(0x68,0x6F+1):            # ENEMY + dots (hardcoded, didn't log them...)
    used_dict[n][i]["cluts"].append(0)


with open(used_cluts_file,"w") as f:
    json.dump(used_dict,f,indent=2)
