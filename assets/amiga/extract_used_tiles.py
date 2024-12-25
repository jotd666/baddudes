import json,os,collections

this_dir = os.path.dirname(os.path.abspath(__file__))
used_dict = {}
used_cluts_file = os.path.join(this_dir,"used_cluts.json")
##if os.path.exists(used_cluts_file):
##    with open(used_cluts_file) as f:
##        used_dict = json.load(f)

tiles_dir = os.path.join(this_dir,"tiles")
for n in os.listdir(tiles_dir):
    tiles_file = os.path.join(tiles_dir,n)
    with open(tiles_file,"rb") as f:
        contents = f.read()

    used_tiles = collections.defaultdict(list)

    tile_index = 0
    for offset in range(0,len(contents),16):
        if tile_index:
            block = contents[offset:offset+16]
            for i,c in enumerate(block):
                if c:
                    used_tiles[tile_index].append(i)
        tile_index += 1

    used_dict[n] = used_tiles

with open(used_cluts_file,"w") as f:
    json.dump(used_dict,f,indent=2)
