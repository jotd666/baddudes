import json,os,collections,pathlib

this_dir = pathlib.Path(__file__).absolute().parent
used_dict = {}

used_cluts_file = this_dir / "used_sprite_cluts.json"





used_graphics_dir = this_dir / "used_graphics"

tiles_dir = used_graphics_dir / "sprites"

for n in os.listdir(tiles_dir):
    tiles_file = tiles_dir / n
    with open(tiles_file,"rb") as f:
        contents = f.read()

    used_tiles = collections.defaultdict(lambda : collections.defaultdict(list))

    tile_index = 0
    for offset in range(0,len(contents),16):
        if tile_index:
            block = contents[offset:offset+16]
            for i,c in enumerate(block):
                if c:
                    used_tiles[tile_index]["cluts"].append(i)
                    used_tiles[tile_index]["attributes"] = c & 0x7F  # discard bit 7

        tile_index += 1

    used_dict[n] = used_tiles

# glasse & guy face, ripped manually from code, not a lot of sprites
used_dict["game_intro"] = {x:{"cluts":[0xD if x==0xBBD else 0xE],"attributes":0} for x in range(0xBB8,0xBC0)}

with open(used_cluts_file,"w") as f:
    json.dump(used_dict,f,indent=2)
