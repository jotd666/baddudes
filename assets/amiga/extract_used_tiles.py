import json,os,collections,pathlib

this_dir = pathlib.Path(__file__).absolute().parent
used_dict = {}
dropped_tile_index = set()

used_cluts_file = this_dir / "used_cluts.json"

# get dude tiles (big dude pics in intro) and don't consider their tiles
for i in range(2):
    with open(this_dir / f"dudes_{i}_tiles","rb") as f:
        f.seek(0x380)       # consider first tiles as used
        contents = f.read()
        for j in range(0,len(contents),2):
            tile_index = ((contents[j]<<8)+contents[j+1])&0xFFF
            if tile_index > 0x100:
                dropped_tile_index.add(tile_index)


##if os.path.exists(used_cluts_file):
##    with open(used_cluts_file) as f:
##        used_dict = json.load(f)

tiles_dir = this_dir / "tiles"
for n in os.listdir(tiles_dir):
    tiles_file = tiles_dir / n
    with open(tiles_file,"rb") as f:
        contents = f.read()

    used_tiles = collections.defaultdict(list)

    tile_index = 0
    for offset in range(0,len(contents),16):
        if tile_index and (n != "title_244000" or tile_index not in dropped_tile_index):
            block = contents[offset:offset+16]
            for i,c in enumerate(block):
                if c:
                    used_tiles[tile_index].append(i)
        tile_index += 1

    used_dict[n] = used_tiles

# force use of clut 0 for all letters & numbers in tileset 244000
n = "title_244000"
for i in range(ord("A"),ord("Z")+1):
    used_dict[n][i].append(0)
for i in range(ord("0"),ord("9")+1):
    used_dict[n][i].append(0)

# only 4 tiles are used for background. Character is too costly in colors (32)
# besides it also uses sprites for glasses & mouth. We'll see later

used_dict["tiles_game_intro_24A000"] = {k:[3] for k in range(0x6A0,0x6A4)}

with open(used_cluts_file,"w") as f:
    json.dump(used_dict,f,indent=2)
