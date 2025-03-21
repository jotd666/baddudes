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
     0xAAE,0xAAC,0xAB0,0xab6,  # elevator door parts
    }


    special_2x_4x_dual = set()

    # glasses & guy face, ripped manually from code, not a lot of sprites
    used_dict[game_intro] = {x:{"cluts":[0xD if x==0xBBD else 0xE],"attributes":0} for x in range(0xBB8,0xBC0)}
    for k,d in used_dict.items():
        if k != "game_intro":
            # just clone the entries and zero attributes
            new_d = {}
            for k,v in d.items():
                ik = int(k)
                vattr = v["attributes"]
                if ik in extra_single_size or (vattr & 0x40 and vattr & 0x18) or (vattr & 0x18 == 0x18):
                    # dual tile if:
                    # 1) manual declaration of single tile (mask is 0 in that case so logged or not... not seen)
                    # 2) used as Y-flipped and multi as well as if multi, Y-flipped version won't match (tile order doesn't change) so they
                    # have to use the single tiles instead. If we only generate the multi-tile, then
                    # the flipped/single version will be missing
                    # 3) if attributes are fake 8x, actually 4x ORed with 2x (0x18), we have dual multi-tiled sprites usage
                    # (rare case, but happens with lots of bosses: karnov, akaikage, devil pole, giving them 4 feet or a 3rd leg - yuck
                    # if we display the highest tile all the time). 2x: body, 4x: body+feet position 1. So when displaying feet position 2
                    # the 4x body+feet position 1 is displayed and ... 3RD LEG!!
                    vc = v.copy()
                    if vattr & 0x18 == 0x18:
                        vc["attributes"] = 8
                        v["attributes"] = 0x10
                        special_2x_4x_dual.add(ik)
                    else:
                        vc["attributes"] = 0  # 16x16 manual declare or Y flip multi

                    new_d[k] = vc
                    k += 0x1000    # offset for dual tile
                new_d[k] = v

            d.update(new_d)

    with open(multi_dual_sprite_tiles_file,"w") as f:
        # special special tiles (boss parts, mainly)
        json.dump(sorted(special_2x_4x_dual),f,indent=2)

    with open(this_dir / "shared_sprite_cluts.json") as f:
        # this file has been extracted from a complete list of player moves
        # bonuses/weapons as well
        player_moves = json.load(f)
        # to do the second player, duplicate entries with clut 1
        # not activated, as it uses too many palette entries
##        for k,v in player_moves.items():
##            if (0 <= int(k) < 0x200) or (0x800 < int(k) < 0x825):
##                v["cluts"].append(1)

    for k,v in used_dict.items():
        if k.startswith("game_level_"):
            v.update(player_moves)

    with open(used_cluts_file,"w") as f:
        json.dump(used_dict,f,indent=2)

if __name__ == "__main__":
    doit()
