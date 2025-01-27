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
                    # discard bit 7 (7: active sprite)
                    used_tiles[tile_index]["attributes"] = c & 0x7F

        tile_index += 1

    used_dict[n] = used_tiles

game_intro = "game_intro"

extra_single_size = {
0xC,  # player head part (used in nunchuck)
0x32,0x30,  # crouched player head part (used in nunchuck)

}

# glasses & guy face, ripped manually from code, not a lot of sprites
used_dict[game_intro] = {x:{"cluts":[0xD if x==0xBBD else 0xE],"attributes":0} for x in range(0xBB8,0xBC0)}
for k,d in used_dict.items():
    if k != "game_intro":
        # just clone the entries and zero attributes
        new_d = {}
        for k,v in d.items():
            ik = int(k)
            if ik in extra_single_size or (v["attributes"] & 0x40 and v["attributes"] & 0x18):
                # used as Y-flipped and multi as well we should also declare single tile, as
                # if multi, Y-flipped version won't match (tile order doesn't change) so they
                # have to use the single tiles instead. If we only generate the multi-tile, then
                # the flipped/single version will be missing
                vc = v.copy()
                vc["attributes"] = 0  # simple 16x16
                new_d[k] = vc
                k += 0x1000    # offset for non-16x16 tile
            new_d[k] = v
        d.update(new_d)

with open(used_cluts_file,"w") as f:
    json.dump(used_dict,f,indent=2)
