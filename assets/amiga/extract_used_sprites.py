import json,os,collections,pathlib

from shared import *
used_dict = {}

used_cluts_file = used_sprite_cluts_file



tiles_dir = used_graphics_dir / "sprites"

def doit():
    side_grouped_dict,vert_grouped_dict = load_grouped_dicts()


    # those tiles should not appear alone, their data is used as grouped with primary tile
    discarded_grouped_tiles = {x for v in list(side_grouped_dict.values())+list(vert_grouped_dict.values()) for x in v}


    for n in os.listdir(tiles_dir):
        tiles_file = tiles_dir / n
        with open(tiles_file,"rb") as f:
            contents = f.read()

        used_tiles = collections.defaultdict(lambda : collections.defaultdict(list))

        tile_index = 0
        for offset in range(0,len(contents),16):
            if tile_index and tile_index not in discarded_grouped_tiles:
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
    0x470,      # karnov head
    0x64C,0x64E,0x650,  # boss 2 parts
     0x980,  # animal head
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

    with open(this_dir / "shared_sprite_cluts.json") as f:
        # this file has been extracted from a complete list of player moves
        # bonuses/weapons as well
        player_moves = json.load(f)
    for k,v in used_dict.items():
        if k.startswith("game_level_"):
            v.update(player_moves)

    with open(used_cluts_file,"w") as f:
        json.dump(used_dict,f,indent=2)

if __name__ == "__main__":
    doit()
