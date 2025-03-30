from PIL import Image,ImageOps
import os,struct,glob,bitplanelib,json,collections

#dev 1 set 0: sprites:
#pal 0: player 1, white ninja
#pal 1: player 2, green ninja
#pal 2: blue ninjas
#pal 3: gray ninjas
#pal F: red ninjas, karnov

dump_images = True


def load_tileset(image_name,side,tileset_name,dumpdir,used_tiles=None,dump=False,name_dict=None):

    if isinstance(image_name,str):
        full_image_path = os.path.join(this_dir,os.path.pardir,"elevator",
                            tile_type,image_name)
        tiles_1 = Image.open(full_image_path)
    else:
        tiles_1 = image_name
    nb_rows = tiles_1.size[1] // side
    nb_cols = tiles_1.size[0] // side


    tileset_1 = []

    if dump:
        dump_subdir = os.path.join(dumpdir,tile_type,tileset_name)
        if tile_offset == 0:
            ensure_empty(dump_subdir)

    tile_number = 0
    palette = set()

    for j in range(nb_rows):
        for i in range(nb_cols):
            if used_tiles and tile_number not in used_tiles:
                tileset_1.append(None)
            else:

                img = Image.new("RGB",(side,side))
                img.paste(tiles_1,(-i*side,-j*side))

                # only consider colors of used tiles
                #palette.update(set(bitplanelib.palette_extract(img)))



                tileset_1.append(img)
                if dump:
                    img = ImageOps.scale(img,5,resample=Image.Resampling.NEAREST)
                    if name_dict:
                        name = name_dict.get(tile_number+tile_offset,"unknown")
                    else:
                        name = "unknown"

                    img.save(os.path.join(dump_subdir,f"{name}_{tile_number+tile_offset:02x}.png"))

            tile_number += 1
    #sorted(set(palette)),
    return tileset_1

name_template = "pal_{pal:02x}.png"

this_dir = os.path.dirname(os.path.abspath(__file__))

tilesdir = os.path.join(this_dir,"sheets","sprites")

dump_dir = os.path.join(this_dir,"dumps")
if not os.path.exists(dump_dir):
    os.mkdir(dump_dir)
for subdir in ["unknown","known"]:
    subdump_dir = os.path.join(dump_dir,subdir)
    if os.path.isdir(subdump_dir):
        for x in glob.glob(os.path.join(subdump_dir,"*.png")):
            os.remove(x)
    else:
        os.mkdir(subdump_dir)

dev = 1
st = 0
blue_ninja_pal = 2

# this script reads the binary ROM and decodes the assembled pics made of sprites into images

with open(r"K:\jff\AmigaHD\PROJETS\GameRelocs\BadDudes\bad_dudes_ref","rb") as f:
    prog = f.read()

table_address = 0x5219c
table_address_end = 0x52f54

assembled_sprites = [struct.unpack_from(">I",prog,offset)[0] for offset in range(table_address,table_address_end,4)]

sprite_info = {
 0x52f54: {'name':'player'},
 0x52f66: {'name':'player'},
 0x52f78: {'name':'player'},
 0x52f8a: {'name':'player'},
 0x52f9c: {'name':'player'},
 0x52fae: {'name':'player'},
 0x52fd0: {'name':'player'},
 0x52fe2: {'name':'player'},
 0x53004: {'name':'player'},
 0x53036: {'name':'player'},
 0x53048: {'name':'player'},
 0x5306a: {'name':'player'},
 0x5307c: {'name':'player'},
 0x5308e: {'name':'player'},
 0x530b0: {'name':'player'},  # broken
 0x530e2: {'name':'player'},  # broken
 0x53114: {'name':'player'},
 0x53136: {'name':'player'},
 0x53158: {'name':'player'},
 0x5317a: {'name':'player'},
 0x5319c: {'name':'player'},
 0x531b6: {'name':'player'},
 0x531d8: {'name':'player'},
 0x5320a: {'name':'player'},
 0x53234: {'name':'player'},
 0x5325e: {'name':'player'},
 0x53288: {'name':'player'},
 0x5329a: {'name':'player'},
 0x532ac: {'name':'player'},
 0x532c6: {'name':'player'},
 0x532e8: {'name':'player'},
 0x5330a: {'name':'player'},
 0x5332c: {'name':'player'},
 0x53356: {'name':'player'},
 0x53380: {'name':'player'},
 0x533b2: {'name':'player'},
 0x533c4: {'name':'player'},
 0x533ee: {'name':'player'},
 0x53420: {'name':'player'},
 0x53442: {'name':'player'},
 0x53464: {'name':'player'},
 0x5348e: {'name':'player'},
 0x534b8: {'name':'player'},
 0x534e2: {'name':'player'},
 0x53504: {'name':'player'},
 0x53526: {'name':'player'},
 0x53538: {'name':'player'},
 0x5355a: {'name':'player'},
 0x53584: {'name':'player'},
 0x535ae: {'name':'player'},
 0x535f0: {'name':'player'},
 0x53612: {'name':'player'},
 0x53654: {'name':'player'},
 0x5367e: {'name':'player'},
 0x536a0: {'name':'player'},
 0x536ba: {'name':'player'},
 0x536dc: {'name':'player'},
 0x536fe: {'name':'player'},
 0x53720: {'name':'player'},
 0x53742: {'name':'player'},
 0x53764: {'name':'player'},
 0x53786: {'name':'on_fire'},
 0x53798: {'name':'on_fire'},
 0x537aa: {'name':'on_fire'},
 0x537bc: {'name':'on_fire'},
 0x537ce: {'name':'on_fire'},
 0x537e0: {'name':'on_fire'},
 0x537f2: {'name':'on_fire'},
 0x53804: {'name':'unknown'},
 0x53816: {'name':'unknown'},
 0x53828: {'name':'wheel'},
 0x5383a: {'name':'unknown'},
 0x5384c: {'name':'unknown'},
 0x5385e: {'name':'player'},
 0x53888: {'name':'player'},
 0x538b2: {'name':'player'},
 0x538dc: {'name':'player'},
 0x5390e: {'name':'player'},
 0x53938: {'name':'player'},
 0x53972: {'name':'player'},
 0x539a4: {'name':'player'},
 0x539c6: {'name':'player'},
 0x539f0: {'name':'player'},
 0x53a12: {'name':'player'},
 0x53a44: {'name':'player'},
 0x53a6e: {'name':'player'},
 0x53a98: {'name':'player'},
 0x53ada: {'name':'player'},
 0x53b14: {'name':'player'},
 0x53b56: {'name':'player'},
 0x53b98: {'name':'player'},
 0x53bd2: {'name':'unknown'},
 0x53bdc: {'name':'ninja'},
 0x53c0e: {'name':'ninja'},
 0x53c40: {'name':'ninja'},
 0x53c72: {'name':'ninja'},
 0x53ca4: {'name':'ninja'},
 0x53cc6: {'name':'ninja'},
 0x53ce8: {'name':'ninja'},
 0x53d0a: {'name':'ninja'},
 0x53d24: {'name':'ninja'},
 0x53d46: {'name':'ninja'},  # broken
 0x53d70: {'name':'ninja'},  # broken
 0x53da2: {'name':'ninja'},
 0x53dbc: {'name':'flipping_ninja'},
 0x53dce: {'name':'flipping_ninja'},
 0x53e00: {'name':'flipping_ninja'},
 0x53e2a: {'name':'flipping_ninja'},
 0x53e44: {'name':'flipping_ninja'},
 0x53e5e: {'name':'flipping_ninja'},
 0x53e88: {'name':'praying_ninja'},
 0x53eaa: {'name':'ninja'},
 0x53ec4: {'name':'ninja'},
 0x53eee: {'name':'ninja'},
 0x53f18: {'name':'ninja'},
 0x53f42: {'name':'ninja'},
 0x53f64: {'name':'ninja'},
 0x53f86: {'name':'ninja'},
 0x53fb0: {'name':'ninja'},
 0x53fda: {'name':'ninja'},
 0x53fec: {'name':'ninja'},
 0x53ffe: {'name':'ninja'},
 0x54020: {'name':'ninja'},
 0x54042: {'name':'ninja'},
 0x54054: {'name':'ninja'},
 0x5407e: {'name':'ninja'},
 0x540a0: {'name':'ninja'},
 0x540ca: {'name':'ninja'},
 0x540fc: {'name':'ninja'},
 0x5412e: {'name':'ninja'},
 0x54150: {'name':'ninja'},
 0x54182: {'name':'ninja'},
 0x541a4: {'name':'dead_ninja'},
 0x541c6: {'name':'pole_ninja'},
 0x541f0: {'name':'ninja'},
 0x54202: {'name':'ninja'},
 0x54234: {'name':'ninja'},
 0x54246: {'name':'ninja'},
 0x54258: {'name':'ninja'},
 0x5426a: {'name':'ninja'},
 0x5427c: {'name':'upside_down_ninja'},
 0x5428e: {'name':'ninja'},
 0x542b8: {'name':'ninja'},
 0x542ca: {'name':'ninja'},
 0x542ec: {'name':'explosion'},
 0x542fe: {'name':'explosion'},
 0x54310: {'name':'explosion'},
 0x54322: {'name':'explosion'},
 0x54334: {'name':'explosion'},
 0x54346: {'name':'explosion'},
 0x54358: {'name':'explosion'},
 0x5436a: {'name':'unknown'},
 0x5437c: {'name':'unknown'},
 0x5438e: {'name':'unknown'},
 0x543a0: {'name':'climbing_ninja'},
 0x543ba: {'name':'climbing_ninja'},
 0x543dc: {'name':'climbing_ninja'},
 0x543fe: {'name':'climbing_ninja'},
 0x54430: {'name':'climbing_ninja'},
 0x544c0: {'name':'ninja_appearing'},
 0x544d2: {'name':'ninja_appearing'},
 0x544e4: {'name':'ninja_appearing'},
 0x544f6: {'name':'praying_ninja'},
 0x54518: {'name':'unknown'},
 0x5452a: {'name':'unknown'},
 0x5454c: {'name':'smoke'},
 0x5456e: {'name':'unknown'},
 0x545b0: {'name':'smoke'},
 0x545f2: {'name':'nunchuck_ninja'},
 0x54614: {'name':'sabreman'},
 0x54626: {'name':'sabreman'},
 0x54638: {'name':'sabreman'},
 0x54662: {'name':'sabreman'},
 0x5468c: {'name':'sabreman'},
 0x546b6: {'name':'sabreman'},
 0x546e0: {'name':'sabreman'},
 0x5470a: {'name':'sabreman'},
 0x54734: {'name':'sabreman'},
 0x54766: {'name':'sabreman'},
 0x547a8: {'name':'sabreman'},
 0x547d2: {'name':'sabreman'},
 0x547fc: {'name':'sabreman'},
 0x5482e: {'name':'sabreman'},
 0x54870: {'name':'sabreman'},
 0x548aa: {'name':'sabreman'},
 0x548d4: {'name':'sabreman'},
 0x548fe: {'name':'sabreman'},
 0x54930: {'name':'sabreman'},
 0x54952: {'name':'smoke'},
 0x54984: {'name':'smoke'},
 0x549b6: {'name':'female_ninja'},
 0x549c8: {'name':'female_ninja'},
 0x549da: {'name':'female_ninja'},
 0x549ec: {'name':'female_ninja'},
 0x549fe: {'name':'female_ninja'},
 0x54a10: {'name':'female_ninja'},
 0x54a32: {'name':'female_ninja'},
 0x54a5c: {'name':'female_ninja'},
 0x54a8e: {'name':'female_ninja'},
 0x54ab0: {'name':'female_ninja'},
 0x54aca: {'name':'female_ninja'},
 0x54aec: {'name':'female_ninja'},
 0x54b1e: {'name':'female_ninja'},
 0x54b50: {'name':'female_ninja'},
 0x54b82: {'name':'female_ninja'},
 0x54b94: {'name':'female_ninja'},
 0x54bbe: {'name':'female_ninja'},
 0x54be0: {'name':'female_ninja'},
 0x54bf2: {'name':'female_ninja'},
 0x54c0c: {'name':'female_ninja'},
 0x54c3e: {'name':'female_ninja'},
 0x54c50: {'name':'female_ninja'},
 0x54c72: {'name':'female_ninja'},
 0x54c94: {'name':'female_ninja'},
 0x54cb6: {'name':'female_ninja'},
 0x54cd0: {'name':'female_ninja'},
 0x54cf2: {'name':'female_ninja'},
 0x54d04: {'name':'female_ninja'},
 0x54d16: {'name':'female_ninja'},
 0x54d28: {'name':'female_ninja'},
 0x54d3a: {'name':'fire_ninja'},
 0x54d4c: {'name':'fire_ninja'},
 0x54d5e: {'name':'fire_ninja'},
 0x54d70: {'name':'fire_ninja'},
 0x54d82: {'name':'fire_ninja'},
 0x54d94: {'name':'fire_ninja'},
 0x54da6: {'name':'fire_ninja'},
 0x54dd8: {'name':'fire_ninja'},
 0x54e0a: {'name':'fire_ninja'},
 0x54e3c: {'name':'fire_ninja'},
 0x54e7e: {'name':'fire_ninja'},
 0x54e90: {'name':'small_ninja'},
 0x54eb2: {'name':'small_ninja'},
 0x54ed4: {'name':'small_ninja'},
 0x54ef6: {'name':'small_ninja'},
 0x54f18: {'name':'small_ninja'},
 0x54f42: {'name':'small_ninja'},
 0x54f54: {'name':'small_ninja'},
 0x54f76: {'name':'small_ninja'},
 0x54f98: {'name':'small_ninja'},
 0x54faa: {'name':'small_ninja'},
 0x54fdc: {'name':'small_ninja'},
 0x54ffe: {'name':'small_ninja'},
 0x55020: {'name':'small_ninja'},
 0x55042: {'name':'small_ninja'},
 0x55074: {'name':'small_ninja'},
 0x55096: {'name':'small_ninja'},
 0x550b0: {'name':'small_ninja'},
 0x550ca: {'name':'suv_car'},
 0x5513c: {'name':'suv_car'},
 0x551ae: {'name':'suv_car'},
 0x55220: {'name':'suv_car'},
 0x55292: {'name':'porsche_car'},
 0x5532c: {'name':'porsche_car'},
 0x553c6: {'name':'porsche_car'},
 0x55460: {'name':'porsche_car'},
 0x554fa: {'name':'sedan_car'},
 0x5557c: {'name':'sedan_car'},
 0x555fe: {'name':'sedan_car'},
 0x55680: {'name':'sedan_car'},
 0x55702: {'name':'dog'},
 0x55724: {'name':'dog'},
 0x5574e: {'name':'dog'},
 0x55770: {'name':'dog'},
 0x55792: {'name':'dog'},
 0x557b4: {'name':'dog'},
 0x557d6: {'name':'dog'},
 0x557f8: {'name':'dog'},
 0x5581a: {'name':'dog'},
 0x5583c: {'name':'dog'},
 0x5585e: {'name':'karnov'},
 0x55878: {'name':'karnov'},
 0x558a2: {'name':'karnov'},
 0x558d4: {'name':'karnov'},
 0x5591e: {'name':'karnov'},
 0x55960: {'name':'karnov'},
 0x55992: {'name':'karnov'},
 0x559d4: {'name':'karnov'},
 0x55a06: {'name':'karnov'},  # broken
 0x55a60: {'name':'karnov'},  # broken
 0x55aba: {'name':'karnov'},
 0x55adc: {'name':'karnov'},
 0x55b0e: {'name':'karnov'},
 0x55b40: {'name':'karnov'},
 0x55b8a: {'name':'karnov'},
 0x55bbc: {'name':'karnov'},
 0x55bd6: {'name':'karnov'},
 0x55c08: {'name':'karnov'},
 0x55c4a: {'name':'karnov'},
 0x55c94: {'name':'ninja_boss'},
 0x55cc6: {'name':'ninja_boss'},
 0x55cf0: {'name':'ninja_boss'},
 0x55d22: {'name':'ninja_boss'},
 0x55d4c: {'name':'ninja_boss'},
 0x55d86: {'name':'ninja_boss'},
 0x55dc0: {'name':'ninja_boss'},
 0x55e02: {'name':'ninja_boss'},
 0x55e3c: {'name':'ninja_boss'},
 0x55e5e: {'name':'ninja_boss'},
 0x55e80: {'name':'ninja_boss'},
 0x55eb2: {'name':'ninja_boss'},
 0x55eec: {'name':'ninja_boss'},
 0x55f16: {'name':'ninja_boss'},
 0x55f48: {'name':'ninja_boss'},
 0x55f72: {'name':'devil_pole'},
 0x55f8c: {'name':'devil_pole'},
 0x55fb6: {'name':'devil_pole'},
 0x55fe0: {'name':'devil_pole'},
 0x5600a: {'name':'devil_pole'},
 0x56044: {'name':'devil_pole'},
 0x56066: {'name':'devil_pole'},
 0x560a0: {'name':'devil_pole'},
 0x560da: {'name':'devil_pole'},
 0x5610c: {'name':'devil_pole'},
 0x5613e: {'name':'devil_pole'},
 0x56160: {'name':'devil_pole'},
 0x5617a: {'name':'devil_pole'},
 0x561a4: {'name':'devil_pole'},
 0x561d6: {'name':'devil_pole'},
 0x56200: {'name':'devil_pole'},
 0x5622a: {'name':'boss_4'},
 0x5625c: {'name':'boss_4'},
 0x5627e: {'name':'boss_4'},
 0x562b0: {'name':'boss_4'},
 0x562e2: {'name':'boss_4'},
 0x5632c: {'name':'boss_4'},
 0x56376: {'name':'boss_4'},
 0x563c0: {'name':'boss_4'},
 0x5640a: {'name':'boss_4'},
 0x5643c: {'name':'boss_4'},
 0x5648e: {'name':'boss_4'},
 0x564c8: {'name':'boss_4'},
 0x564fa: {'name':'boss_4'},
 0x5655c: {'name':'boss_4'},
 0x565ae: {'name':'boss_4'},
 0x565e8: {'name':'boss_4'},
 0x56632: {'name':'boss_4'},
 0x56674: {'name':'boss_4'},
 0x566a6: {'name':'boss_4'},
 0x566d8: {'name':'boss_4'},
 0x5670a: {'name':'boss_4'},
 0x56724: {'name':'akaikage'},
 0x56746: {'name':'akaikage'},
 0x56770: {'name':'akaikage'},
 0x5679a: {'name':'akaikage'},
 0x567c4: {'name':'akaikage'},
 0x567ee: {'name':'akaikage'},
 0x56818: {'name':'akaikage'},
 0x56842: {'name':'akaikage'},
 0x56874: {'name':'akaikage'},
 0x568a6: {'name':'akaikage'},
 0x568e8: {'name':'akaikage'},
 0x56932: {'name':'akaikage'},
 0x5694c: {'name':'akaikage'},
 0x56986: {'name':'akaikage'},
 0x56998: {'name':'akaikage'},
 0x569ca: {'name':'akaikage'},
 0x569ec: {'name':'dragonninja'},
 0x56a1e: {'name':'dragonninja'},
 0x56a60: {'name':'dragonninja'},
 0x56aaa: {'name':'dragonninja'},
 0x56b04: {'name':'dragonninja'},
 0x56b66: {'name':'dragonninja'},
 0x56bb8: {'name':'dragonninja'},
 0x56c0a: {'name':'dragonninja'},
 0x56c74: {'name':'dragonninja'},
 0x56cde: {'name':'dragonninja'},
 0x56d38: {'name':'dragonninja'},
 0x56d92: {'name':'dragonninja'},
 0x56dcc: {'name':'dragonninja'},
 0x56df6: {'name':'unknown'},
 0x57020: {'name':'unknown'},
 0x5702a: {'name':'unknown'},
 0x57034: {'name':'unknown'},
 0x5703e: {'name':'unknown'},
 0x57048: {'name':'unknown'},
 0x5705a: {'name':'unknown'},
 0x5706c: {'name':'unknown'},
 0x57076: {'name':'unknown'},
 0x57088: {'name':'unknown'},
 0x5709a: {'name':'unknown'},
 0x570ac: {'name':'nunchuk'},
 0x570be: {'name':'nunchuk'},
 0x570d0: {'name':'nunchuk'},
 0x570e2: {'name':'nunchuk'},
 0x570f4: {'name':'nunchuk'},
 0x57106: {'name':'nunchuk'},
 0x57118: {'name':'nunchuk'},
 0x5712a: {'name':'unknown'},
 0x57134: {'name':'knife'},
 0x5713e: {'name':'unknown'},
 0x57148: {'name':'knife'},
 0x57152: {'name':'unknown'},
 0x5715c: {'name':'unknown'},
 0x57166: {'name':'knife'},
 0x57170: {'name':'unknown'},
 0x5717a: {'name':'unknown'},
 0x57184: {'name':'unknown'},
 0x5718e: {'name':'unknown'},
 0x57198: {'name':'unknown'},
 0x571a2: {'name':'unknown'},
 0x571ac: {'name':'unknown'},
 0x571b6: {'name':'unknown'},
 0x571c0: {'name':'unknown'},
 0x571ca: {'name':'unknown'},
 0x571d4: {'name':'unknown'},
 0x571de: {'name':'unknown'},
 0x571e8: {'name':'unknown'},
 0x571f2: {'name':'unknown'},
 0x571fc: {'name':'unknown'},
 0x57206: {'name':'unknown'},
 0x57210: {'name':'unknown'},
 0x5721a: {'name':'unknown'},
 0x57224: {'name':'smoke'},
 0x57236: {'name':'unknown'},
 0x57258: {'name':'unknown'},
 0x5727a: {'name':'unknown'},
 0x5729c: {'name':'unknown'},
 0x572be: {'name':'unknown'},
 0x572c8: {'name':'unknown'},
 0x572d2: {'name':'time'},
 0x572dc: {'name':'time'},
 0x572e6: {'name':'nunchuk'},
 0x572f0: {'name':'nunchuk'},
 0x572fa: {'name':'knife'},
 0x57304: {'name':'knife'},
 0x5730e: {'name':'unknown'},
 0x57318: {'name':'unknown'},
 0x57322: {'name':'unknown'},
 0x5732c: {'name':'unknown'},
 0x57336: {'name':'unknown'},
 0x57340: {'name':'unknown'},
 0x5734a: {'name':'unknown'},
 0x57354: {'name':'unknown'},
 0x5735e: {'name':'unknown'},
 0x57368: {'name':'star'},
 0x57372: {'name':'star'},
 0x5737c: {'name':'unknown'},
 0x57386: {'name':'star'},
 0x57390: {'name':'grappling'},
 0x573a2: {'name':'grappling'},
 0x573bc: {'name':'unknown'},
 0x573ce: {'name':'unknown'},
 0x573d8: {'name':'unknown'},
 0x573ea: {'name':'unknown'},
 0x57404: {'name':'grappling'},
 0x57416: {'name':'grappling'},
 0x57420: {'name':'unknown'},
 0x5743a: {'name':'unknown'},
 0x57454: {'name':'unknown'},
 0x5745e: {'name':'unknown'},
 0x57470: {'name':'flame'},
 0x5748a: {'name':'unknown'},
 0x574a4: {'name':'unknown'},
 0x574be: {'name':'truck_wheel'},
 0x574d0: {'name':'truck_wheel'},
 0x574e2: {'name':'unknown'},
 0x5752c: {'name':'unknown'},
 0x5754e: {'name':'unknown'},
 0x57580: {'name':'unknown'},
 0x575c2: {'name':'helicopter_blade_axis'},
 0x575d4: {'name':'helicopter_blade_axis'},
 0x575e6: {'name':'helicopter_blade_axis'},
 0x575f8: {'name':'helicopter_blade_axis'},
 0x5760a: {'name':'unknown'},
 0x57654: {'name':'unknown'},
 0x57676: {'name':'unknown'},
 0x576a8: {'name':'unknown'},
 0x576ea: {'name':'unknown'},
 0x576fc: {'name':'unknown'},
 0x5770e: {'name':'elevator_door'},
 0x57790: {'name':'unknown'},
 0x57844: {'name':'unknown'},
 0x578d6: {'name':'unknown'},
 0x578f8: {'name':'unknown'},
 0x5792a: {'name':'elevator_door'},
 0x5793c: {'name':'elevator_door'},
 0x57978: {'name':'unknown'},
 0x5798a: {'name':'unknown'},
 0x57994: {'name':'heli_door'},
 0x5799e: {'name':'heli_door'},
 0x579a8: {'name':'heli_door'},
 0x579ba: {'name':'heli_door'},
 0x579d4: {'name':'ronnie'},
 0x579f6: {'name':'ronnie'},
 0x57a18: {'name':'bad_dude'},
 0x57a6a: {'name':'bad_dude'},  # exactly same as above
 0x57acc: {'name':'ronnie'},
 0x57b1e: {'name':'unknown'},
}


blue_ninja_tiles = Image.open(os.path.join(tilesdir,name_template.format(dev=dev,st=st,pal=blue_ninja_pal)))
red_ninja_tiles = Image.open(os.path.join(tilesdir,name_template.format(dev=dev,st=st,pal=0xF)))
player_tiles = Image.open(os.path.join(tilesdir,name_template.format(dev=dev,st=st,pal=0)))
car_tiles = Image.open(os.path.join(tilesdir,name_template.format(dev=dev,st=st,pal=0xB)))
dog_tiles = Image.open(os.path.join(tilesdir,name_template.format(dev=dev,st=st,pal=0xD)))

red_ninja_tiles = load_tileset(red_ninja_tiles,16,"red_ninjas","dumps")
blue_ninja_tiles = load_tileset(blue_ninja_tiles,16,"ninjas","dumps")
player_tiles = load_tileset(player_tiles,16,"player","dumps")
car_tiles = load_tileset(car_tiles,16,"cars","dumps")
dog_tiles = load_tileset(dog_tiles,16,"dogs","dumps")


def apply_tileset(name,tiles):
    for k,v in sprite_info.items():
        if name in v["name"]:
            v["tiles"] = tiles

apply_tileset("player",player_tiles)
apply_tileset("dog",dog_tiles)
apply_tileset("car",car_tiles)
apply_tileset("heli_door",player_tiles)
apply_tileset("ronnie",player_tiles)

apply_tileset("ninja",blue_ninja_tiles)
apply_tileset("akaikage",blue_ninja_tiles)
apply_tileset("karnov",red_ninja_tiles)
apply_tileset("fire_ninja",red_ninja_tiles)
apply_tileset("dragonninja",red_ninja_tiles)
apply_tileset("on_fire",red_ninja_tiles)

class SpritePtr:
    def __init__(self,h,offset):
        self.height = h
        self.x = [0]*h
        self.y = [0]*h
        self.code = [0]*h
        self.offset = offset
        pass


def decode_sprite(offset):
    info = sprite_info.get(offset,dict())
    sprite_name = info.get("name","unknown")
    tile_set = info.get("tiles",blue_ninja_tiles)

    nb_blocks = prog[offset+1]
    block_size = 8

    result = prog[offset:offset+nb_blocks*block_size+2]

    blocks = result[2:]

    sprite_used_by_entry = collections.defaultdict(list)
    sprite_codes = {}
    sprite_objects = []
    spritelist = []

    for idx,i in enumerate(range(0,block_size*nb_blocks,block_size)):
        offs = 0
        priority = False
        pri_mask = 0
        spriteram = [(blocks[i+j]<<8)+blocks[i+j+1] for j in range(0,block_size,2)]


        data0 = spriteram[offs]
        data2 = spriteram[offs + 2]
        colour = data2 >> 12
    ##        if (priority)
    ##            m_colpri_cb(colour, pri_mask);

        flash = data2 & 0x800

        flipx = data0 & 0x2000
        parentFlipY = flipy = data0 & 0x4000
        h = (1 << ((data0 & 0x1800) >> 11))
        w = (1 << ((data0 & 0x0600) >>  9))


        sx = data2 & 0x01ff;
        sy = data0 & 0x01ff;
        if (sx >= 256):
            sx -= 512
        if (sy >= 256):
            sy -= 512
        sx = 240 - sx
        sy = 240 - sy

        mult = -16

        if (not (spriteram[offs] & 0x8000)):
                offs += 4
                raise Exception("end of sprite list") # doesn't happen here


        for x in range(w):

            # maybe, birdie try appears to specify the base code for each part..
            code = spriteram[offs + 1] & 0x1fff

            code &= ~(h - 1)   # align code on height, make it start in a round number (maybe not necessary!)

            # not affected by flipscreen
            if (parentFlipY): # in the case of multi-width sprites the y flip bit is set by the parent
                incy = -1
            else:

                code += h - 1
                incy = 1


            sprite_ptr = SpritePtr(h,offset)
            if True: # (not flash or (screen.frame_number() & 1))


                sprite_ptr.colour = colour;
                sprite_ptr.flipx = flipx;
                sprite_ptr.flipy = flipy;

                for y in range(h):

                    sprite_ptr.code[y] = code - y * incy
                    sprite_ptr.x[y] = sx + (mult * x)
                    sprite_ptr.y[y] = sy + (mult * y)

                sprite_objects.append(sprite_ptr)




    sprite_image = Image.new("RGB",(128,128))

    for so in sprite_objects:
        for i in range(so.height):
            img = tile_set[so.code[i]]
            sprite_codes[hex(so.code[i])] = sprite_name
            sprite_used_by_entry[hex(so.offset)].append(hex(so.code[i]))
            x = so.x[i]
            y = so.y[i]
            if y > 128:
                y -= 256
            if x > 128:
                x -= 256


            x += 60
            y += 60

            sprite_image.paste(img,(x,y))


    # to get the full width/height of the image, we use the dimensions of autocrop
    # it's hacky, but works because of "transparency" blocks that align the image
    _,sprite_image = bitplanelib.autocrop_x(bitplanelib.autocrop_y(sprite_image)[1])
    dims = sprite_image.size

    subdir = "unknown" if 'unknown' in sprite_name else "known"
    if dump_images:
        sprite_image = ImageOps.scale(sprite_image,5,resample=Image.Resampling.NEAREST)
        sprite_image.save(os.path.join(dump_dir,subdir,f"{sprite_name}_{offset:x}.png"))

    return sprite_codes,sprite_used_by_entry,dims

if True:
    sprite_name_code = {}
    sprite_used_by_entry = {}
    macro_sprite_code_dimensions = []
    for offset in assembled_sprites:  # there are duplicates in that list but we need the order
        sprite_codes,sue,dims = decode_sprite(offset)
        macro_sprite_code_dimensions.append(list(dims))
        sprite_name_code.update(sprite_codes)
        sprite_used_by_entry.update(sue)

    # we generate that table once and for all, it is then git-tracked in the "amiga" subdir
    # so we don't need to run this script when building the project
    with open(os.path.join(this_dir,"amiga","macro_sprite_sizes.json"),"w") as f:
        json.dump(macro_sprite_code_dimensions,f,indent=2)

    with open(os.path.join(this_dir,"sprite_code_names.json"),"w") as f:
        json.dump({"codes_names":sprite_name_code,"sprite_used_by_entry":sprite_used_by_entry},f,indent=2)
#decode_sprite(0x52f8a)
with open(os.path.join(this_dir,"sprite_code_names.json"),"r") as f:
    sprite_used_by_entry = json.load(f)

tile_used_by_block = collections.defaultdict(set)
for k,vl in sprite_used_by_entry["sprite_used_by_entry"].items():
    for v in vl:
        tile_used_by_block[v].add(k)

with open(os.path.join(this_dir,"tiles_used_by_block.json"),"w") as f:
        json.dump({"tile_used_by_block":{k:list(v) for k,v in tile_used_by_block.items()},"tiles_used_once":[k for k,v in tile_used_by_block.items() if len(v)==1]},f,indent=2)
