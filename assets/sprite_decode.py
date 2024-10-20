from PIL import Image,ImageOps
import os,struct,bitplanelib

#dev 1 set 0: sprites:
#pal 0: player 1, white ninja
#pal 1: player 2, green ninja
#pal 2: blue ninjas
#pal 3: gray ninjas
#pal F: red ninjas

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

name_template = "gfx dev {dev} set {st} tiles 16x16 colors 16 pal {pal:02x}.png"

this_dir = os.path.dirname(os.path.abspath(__file__))

tilesdir = os.path.join(this_dir,os.pardir,"mame","baddudes")


dev = 1
st = 0
pal = 2

with open(r"K:\jff\AmigaHD\PROJETS\GameRelocs\BadDudes\bad_dudes_ref","rb") as f:
    prog = f.read()

table_address = 0x5219c
table_address_end = 0x52f54

assembled_sprites = {struct.unpack_from(">I",prog,offset)[0] for offset in range(table_address,table_address_end,4)}

sprite_info = {'0x0x52f54': {'name':'unknown'},
 0x52f66: {'name':'unknown'},
 0x52f78: {'name':'unknown'},
 0x52f8a: {'name':'unknown'},
 0x52f9c: {'name':'unknown'},
 0x52fae: {'name':'unknown'},
 0x52fd0: {'name':'unknown'},
 0x52fe2: {'name':'unknown'},
 0x53004: {'name':'unknown'},
 0x53036: {'name':'unknown'},
 0x53048: {'name':'unknown'},
 0x5306a: {'name':'unknown'},
 0x5307c: {'name':'unknown'},
 0x5308e: {'name':'unknown'},
 0x530b0: {'name':'unknown'},
 0x530e2: {'name':'unknown'},
 0x53114: {'name':'unknown'},
 0x53136: {'name':'unknown'},
 0x53158: {'name':'unknown'},
 0x5317a: {'name':'unknown'},
 0x5319c: {'name':'unknown'},
 0x531b6: {'name':'unknown'},
 0x531d8: {'name':'unknown'},
 0x5320a: {'name':'unknown'},
 0x53234: {'name':'unknown'},
 0x5325e: {'name':'unknown'},
 0x53288: {'name':'unknown'},
 0x5329a: {'name':'unknown'},
 0x532ac: {'name':'unknown'},
 0x532c6: {'name':'unknown'},
 0x532e8: {'name':'unknown'},
 0x5330a: {'name':'unknown'},
 0x5332c: {'name':'unknown'},
 0x53356: {'name':'unknown'},
 0x53380: {'name':'unknown'},
 0x533b2: {'name':'unknown'},
 0x533c4: {'name':'unknown'},
 0x533ee: {'name':'unknown'},
 0x53420: {'name':'unknown'},
 0x53442: {'name':'unknown'},
 0x53464: {'name':'unknown'},
 0x5348e: {'name':'unknown'},
 0x534b8: {'name':'unknown'},
 0x534e2: {'name':'unknown'},
 0x53504: {'name':'unknown'},
 0x53526: {'name':'unknown'},
 0x53538: {'name':'unknown'},
 0x5355a: {'name':'unknown'},
 0x53584: {'name':'unknown'},
 0x535ae: {'name':'unknown'},
 0x535f0: {'name':'unknown'},
 0x53612: {'name':'unknown'},
 0x53654: {'name':'unknown'},
 0x5367e: {'name':'unknown'},
 0x536a0: {'name':'unknown'},
 0x536ba: {'name':'unknown'},
 0x536dc: {'name':'unknown'},
 0x536fe: {'name':'unknown'},
 0x53720: {'name':'unknown'},
 0x53742: {'name':'unknown'},
 0x53764: {'name':'unknown'},
 0x53786: {'name':'unknown'},
 0x53798: {'name':'unknown'},
 0x537aa: {'name':'unknown'},
 0x537bc: {'name':'unknown'},
 0x537ce: {'name':'unknown'},
 0x537e0: {'name':'unknown'},
 0x537f2: {'name':'unknown'},
 0x53804: {'name':'unknown'},
 0x53816: {'name':'unknown'},
 0x53828: {'name':'unknown'},
 0x5383a: {'name':'unknown'},
 0x5384c: {'name':'unknown'},
 0x5385e: {'name':'unknown'},
 0x53888: {'name':'unknown'},
 0x538b2: {'name':'unknown'},
 0x538dc: {'name':'unknown'},
 0x5390e: {'name':'unknown'},
 0x53938: {'name':'unknown'},
 0x53972: {'name':'unknown'},
 0x539a4: {'name':'unknown'},
 0x539c6: {'name':'unknown'},
 0x539f0: {'name':'unknown'},
 0x53a12: {'name':'unknown'},
 0x53a44: {'name':'unknown'},
 0x53a6e: {'name':'unknown'},
 0x53a98: {'name':'unknown'},
 0x53ada: {'name':'unknown'},
 0x53b14: {'name':'unknown'},
 0x53b56: {'name':'unknown'},
 0x53b98: {'name':'unknown'},
 0x53bd2: {'name':'unknown'},
 0x53bdc: {'name':'unknown'},
 0x53c0e: {'name':'unknown'},
 0x53c40: {'name':'unknown'},
 0x53c72: {'name':'running_ninja'},
 0x53ca4: {'name':'unknown'},
 0x53cc6: {'name':'unknown'},
 0x53ce8: {'name':'unknown'},
 0x53d0a: {'name':'unknown'},
 0x53d24: {'name':'unknown'},
 0x53d46: {'name':'unknown'},
 0x53d70: {'name':'unknown'},
 0x53da2: {'name':'unknown'},
 0x53dbc: {'name':'unknown'},
 0x53dce: {'name':'unknown'},
 0x53e00: {'name':'unknown'},
 0x53e2a: {'name':'unknown'},
 0x53e44: {'name':'unknown'},
 0x53e5e: {'name':'unknown'},
 0x53e88: {'name':'unknown'},
 0x53eaa: {'name':'unknown'},
 0x53ec4: {'name':'unknown'},
 0x53eee: {'name':'unknown'},
 0x53f18: {'name':'unknown'},
 0x53f42: {'name':'unknown'},
 0x53f64: {'name':'unknown'},
 0x53f86: {'name':'unknown'},
 0x53fb0: {'name':'unknown'},
 0x53fda: {'name':'unknown'},
 0x53fec: {'name':'unknown'},
 0x53ffe: {'name':'unknown'},
 0x54020: {'name':'unknown'},
 0x54042: {'name':'unknown'},
 0x54054: {'name':'unknown'},
 0x5407e: {'name':'unknown'},
 0x540a0: {'name':'unknown'},
 0x540ca: {'name':'unknown'},
 0x540fc: {'name':'unknown'},
 0x5412e: {'name':'unknown'},
 0x54150: {'name':'unknown'},
 0x54182: {'name':'unknown'},
 0x541a4: {'name':'unknown'},
 0x541c6: {'name':'unknown'},
 0x541f0: {'name':'unknown'},
 0x54202: {'name':'unknown'},
 0x54234: {'name':'unknown'},
 0x54246: {'name':'unknown'},
 0x54258: {'name':'unknown'},
 0x5426a: {'name':'unknown'},
 0x5427c: {'name':'unknown'},
 0x5428e: {'name':'unknown'},
 0x542b8: {'name':'unknown'},
 0x542ca: {'name':'unknown'},
 0x542ec: {'name':'unknown'},
 0x542fe: {'name':'unknown'},
 0x54310: {'name':'unknown'},
 0x54322: {'name':'unknown'},
 0x54334: {'name':'unknown'},
 0x54346: {'name':'unknown'},
 0x54358: {'name':'unknown'},
 0x5436a: {'name':'unknown'},
 0x5437c: {'name':'unknown'},
 0x5438e: {'name':'unknown'},
 0x543a0: {'name':'unknown'},
 0x543ba: {'name':'unknown'},
 0x543dc: {'name':'unknown'},
 0x543fe: {'name':'unknown'},
 0x54430: {'name':'unknown'},
 0x544c0: {'name':'unknown'},
 0x544d2: {'name':'unknown'},
 0x544e4: {'name':'unknown'},
 0x544f6: {'name':'unknown'},
 0x54518: {'name':'unknown'},
 0x5452a: {'name':'unknown'},
 0x5454c: {'name':'unknown'},
 0x5456e: {'name':'unknown'},
 0x545b0: {'name':'unknown'},
 0x545f2: {'name':'unknown'},
 0x54614: {'name':'unknown'},
 0x54626: {'name':'unknown'},
 0x54638: {'name':'unknown'},
 0x54662: {'name':'unknown'},
 0x5468c: {'name':'unknown'},
 0x546b6: {'name':'unknown'},
 0x546e0: {'name':'unknown'},
 0x5470a: {'name':'unknown'},
 0x54734: {'name':'unknown'},
 0x54766: {'name':'unknown'},
 0x547a8: {'name':'unknown'},
 0x547d2: {'name':'unknown'},
 0x547fc: {'name':'unknown'},
 0x5482e: {'name':'unknown'},
 0x54870: {'name':'unknown'},
 0x548aa: {'name':'unknown'},
 0x548d4: {'name':'unknown'},
 0x548fe: {'name':'unknown'},
 0x54930: {'name':'unknown'},
 0x54952: {'name':'unknown'},
 0x54984: {'name':'unknown'},
 0x549b6: {'name':'unknown'},
 0x549c8: {'name':'unknown'},
 0x549da: {'name':'unknown'},
 0x549ec: {'name':'unknown'},
 0x549fe: {'name':'unknown'},
 0x54a10: {'name':'unknown'},
 0x54a32: {'name':'unknown'},
 0x54a5c: {'name':'unknown'},
 0x54a8e: {'name':'unknown'},
 0x54ab0: {'name':'unknown'},
 0x54aca: {'name':'unknown'},
 0x54aec: {'name':'unknown'},
 0x54b1e: {'name':'unknown'},
 0x54b50: {'name':'unknown'},
 0x54b82: {'name':'unknown'},
 0x54b94: {'name':'unknown'},
 0x54bbe: {'name':'unknown'},
 0x54be0: {'name':'unknown'},
 0x54bf2: {'name':'unknown'},
 0x54c0c: {'name':'unknown'},
 0x54c3e: {'name':'unknown'},
 0x54c50: {'name':'unknown'},
 0x54c72: {'name':'unknown'},
 0x54c94: {'name':'unknown'},
 0x54cb6: {'name':'unknown'},
 0x54cd0: {'name':'unknown'},
 0x54cf2: {'name':'unknown'},
 0x54d04: {'name':'unknown'},
 0x54d16: {'name':'unknown'},
 0x54d28: {'name':'unknown'},
 0x54d3a: {'name':'unknown'},
 0x54d4c: {'name':'unknown'},
 0x54d5e: {'name':'unknown'},
 0x54d70: {'name':'unknown'},
 0x54d82: {'name':'unknown'},
 0x54d94: {'name':'unknown'},
 0x54da6: {'name':'unknown'},
 0x54dd8: {'name':'unknown'},
 0x54e0a: {'name':'unknown'},
 0x54e3c: {'name':'unknown'},
 0x54e7e: {'name':'unknown'},
 0x54e90: {'name':'unknown'},
 0x54eb2: {'name':'unknown'},
 0x54ed4: {'name':'unknown'},
 0x54ef6: {'name':'unknown'},
 0x54f18: {'name':'unknown'},
 0x54f42: {'name':'unknown'},
 0x54f54: {'name':'unknown'},
 0x54f76: {'name':'unknown'},
 0x54f98: {'name':'unknown'},
 0x54faa: {'name':'unknown'},
 0x54fdc: {'name':'unknown'},
 0x54ffe: {'name':'unknown'},
 0x55020: {'name':'unknown'},
 0x55042: {'name':'unknown'},
 0x55074: {'name':'unknown'},
 0x55096: {'name':'unknown'},
 0x550b0: {'name':'unknown'},
 0x550ca: {'name':'suv_car'},
 0x5513c: {'name':'unknown'},
 0x551ae: {'name':'suv_car'},
 0x55220: {'name':'unknown'},
 0x55292: {'name':'unknown'},
 0x5532c: {'name':'unknown'},
 0x553c6: {'name':'porsche_car'},
 0x55460: {'name':'unknown'},
 0x554fa: {'name':'sedan_car'},
 0x5557c: {'name':'unknown'},
 0x555fe: {'name':'sedan_car'},
 0x55680: {'name':'unknown'},
 0x55702: {'name':'unknown'},
 0x55724: {'name':'unknown'},
 0x5574e: {'name':'unknown'},
 0x55770: {'name':'unknown'},
 0x55792: {'name':'unknown'},
 0x557b4: {'name':'dog'},
 0x557d6: {'name':'dog'},
 0x557f8: {'name':'dog'},
 0x5581a: {'name':'unknown'},
 0x5583c: {'name':'unknown'},
 0x5585e: {'name':'unknown'},
 0x55878: {'name':'unknown'},
 0x558a2: {'name':'unknown'},
 0x558d4: {'name':'unknown'},
 0x5591e: {'name':'unknown'},
 0x55960: {'name':'unknown'},
 0x55992: {'name':'unknown'},
 0x559d4: {'name':'unknown'},
 0x55a06: {'name':'unknown'},
 0x55a60: {'name':'unknown'},
 0x55aba: {'name':'unknown'},
 0x55adc: {'name':'unknown'},
 0x55b0e: {'name':'unknown'},
 0x55b40: {'name':'unknown'},
 0x55b8a: {'name':'unknown'},
 0x55bbc: {'name':'unknown'},
 0x55bd6: {'name':'unknown'},
 0x55c08: {'name':'unknown'},
 0x55c4a: {'name':'unknown'},
 0x55c94: {'name':'unknown'},
 0x55cc6: {'name':'unknown'},
 0x55cf0: {'name':'unknown'},
 0x55d22: {'name':'unknown'},
 0x55d4c: {'name':'unknown'},
 0x55d86: {'name':'unknown'},
 0x55dc0: {'name':'unknown'},
 0x55e02: {'name':'unknown'},
 0x55e3c: {'name':'unknown'},
 0x55e5e: {'name':'unknown'},
 0x55e80: {'name':'unknown'},
 0x55eb2: {'name':'unknown'},
 0x55eec: {'name':'unknown'},
 0x55f16: {'name':'unknown'},
 0x55f48: {'name':'unknown'},
 0x55f72: {'name':'unknown'},
 0x55f8c: {'name':'unknown'},
 0x55fb6: {'name':'unknown'},
 0x55fe0: {'name':'unknown'},
 0x5600a: {'name':'unknown'},
 0x56044: {'name':'unknown'},
 0x56066: {'name':'unknown'},
 0x560a0: {'name':'unknown'},
 0x560da: {'name':'unknown'},
 0x5610c: {'name':'unknown'},
 0x5613e: {'name':'unknown'},
 0x56160: {'name':'unknown'},
 0x5617a: {'name':'unknown'},
 0x561a4: {'name':'unknown'},
 0x561d6: {'name':'unknown'},
 0x56200: {'name':'unknown'},
 0x5622a: {'name':'unknown'},
 0x5625c: {'name':'unknown'},
 0x5627e: {'name':'unknown'},
 0x562b0: {'name':'unknown'},
 0x562e2: {'name':'unknown'},
 0x5632c: {'name':'unknown'},
 0x56376: {'name':'unknown'},
 0x563c0: {'name':'unknown'},
 0x5640a: {'name':'unknown'},
 0x5643c: {'name':'unknown'},
 0x5648e: {'name':'unknown'},
 0x564c8: {'name':'unknown'},
 0x564fa: {'name':'unknown'},
 0x5655c: {'name':'unknown'},
 0x565ae: {'name':'unknown'},
 0x565e8: {'name':'unknown'},
 0x56632: {'name':'unknown'},
 0x56674: {'name':'unknown'},
 0x566a6: {'name':'unknown'},
 0x566d8: {'name':'unknown'},
 0x5670a: {'name':'unknown'},
 0x56724: {'name':'unknown'},
 0x56746: {'name':'unknown'},
 0x56770: {'name':'unknown'},
 0x5679a: {'name':'unknown'},
 0x567c4: {'name':'unknown'},
 0x567ee: {'name':'unknown'},
 0x56818: {'name':'unknown'},
 0x56842: {'name':'unknown'},
 0x56874: {'name':'unknown'},
 0x568a6: {'name':'unknown'},
 0x568e8: {'name':'unknown'},
 0x56932: {'name':'unknown'},
 0x5694c: {'name':'unknown'},
 0x56986: {'name':'unknown'},
 0x56998: {'name':'unknown'},
 0x569ca: {'name':'unknown'},
 0x569ec: {'name':'unknown'},
 0x56a1e: {'name':'unknown'},
 0x56a60: {'name':'unknown'},
 0x56aaa: {'name':'unknown'},
 0x56b04: {'name':'unknown'},
 0x56b66: {'name':'unknown'},
 0x56bb8: {'name':'unknown'},
 0x56c0a: {'name':'unknown'},
 0x56c74: {'name':'unknown'},
 0x56cde: {'name':'unknown'},
 0x56d38: {'name':'unknown'},
 0x56d92: {'name':'unknown'},
 0x56dcc: {'name':'unknown'},
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
 0x570ac: {'name':'unknown'},
 0x570be: {'name':'unknown'},
 0x570d0: {'name':'unknown'},
 0x570e2: {'name':'unknown'},
 0x570f4: {'name':'unknown'},
 0x57106: {'name':'unknown'},
 0x57118: {'name':'unknown'},
 0x5712a: {'name':'unknown'},
 0x57134: {'name':'unknown'},
 0x5713e: {'name':'unknown'},
 0x57148: {'name':'unknown'},
 0x57152: {'name':'unknown'},
 0x5715c: {'name':'unknown'},
 0x57166: {'name':'unknown'},
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
 0x57224: {'name':'unknown'},
 0x57236: {'name':'unknown'},
 0x57258: {'name':'unknown'},
 0x5727a: {'name':'unknown'},
 0x5729c: {'name':'unknown'},
 0x572be: {'name':'unknown'},
 0x572c8: {'name':'unknown'},
 0x572d2: {'name':'unknown'},
 0x572dc: {'name':'unknown'},
 0x572e6: {'name':'unknown'},
 0x572f0: {'name':'unknown'},
 0x572fa: {'name':'unknown'},
 0x57304: {'name':'unknown'},
 0x5730e: {'name':'unknown'},
 0x57318: {'name':'unknown'},
 0x57322: {'name':'unknown'},
 0x5732c: {'name':'unknown'},
 0x57336: {'name':'unknown'},
 0x57340: {'name':'unknown'},
 0x5734a: {'name':'unknown'},
 0x57354: {'name':'unknown'},
 0x5735e: {'name':'unknown'},
 0x57368: {'name':'unknown'},
 0x57372: {'name':'unknown'},
 0x5737c: {'name':'unknown'},
 0x57386: {'name':'unknown'},
 0x57390: {'name':'unknown'},
 0x573a2: {'name':'unknown'},
 0x573bc: {'name':'unknown'},
 0x573ce: {'name':'unknown'},
 0x573d8: {'name':'unknown'},
 0x573ea: {'name':'unknown'},
 0x57404: {'name':'unknown'},
 0x57416: {'name':'unknown'},
 0x57420: {'name':'unknown'},
 0x5743a: {'name':'unknown'},
 0x57454: {'name':'unknown'},
 0x5745e: {'name':'unknown'},
 0x57470: {'name':'unknown'},
 0x5748a: {'name':'unknown'},
 0x574a4: {'name':'unknown'},
 0x574be: {'name':'unknown'},
 0x574d0: {'name':'unknown'},
 0x574e2: {'name':'unknown'},
 0x5752c: {'name':'unknown'},
 0x5754e: {'name':'unknown'},
 0x57580: {'name':'unknown'},
 0x575c2: {'name':'unknown'},
 0x575d4: {'name':'unknown'},
 0x575e6: {'name':'unknown'},
 0x575f8: {'name':'unknown'},
 0x5760a: {'name':'unknown'},
 0x57654: {'name':'unknown'},
 0x57676: {'name':'unknown'},
 0x576a8: {'name':'unknown'},
 0x576ea: {'name':'unknown'},
 0x576fc: {'name':'unknown'},
 0x5770e: {'name':'unknown'},
 0x57790: {'name':'unknown'},
 0x57844: {'name':'unknown'},
 0x578d6: {'name':'unknown'},
 0x578f8: {'name':'unknown'},
 0x5792a: {'name':'unknown'},
 0x5793c: {'name':'unknown'},
 0x57978: {'name':'unknown'},
 0x5798a: {'name':'unknown'},
 0x57994: {'name':'unknown'},
 0x5799e: {'name':'unknown'},
 0x579a8: {'name':'unknown'},
 0x579ba: {'name':'unknown'},
 0x579d4: {'name':'unknown'},
 0x579f6: {'name':'unknown'},
 0x57a18: {'name':'unknown'},
 0x57a6a: {'name':'unknown'},
 0x57acc: {'name':'unknown'},
 0x57b1e: {'name':'unknown'},
}


blue_ninja_tiles = Image.open(os.path.join(tilesdir,name_template.format(dev=dev,st=st,pal=pal)))

tiles = load_tileset(blue_ninja_tiles,16,"ninjas","dumps")

class SpritePtr:
    def __init__(self,h):
        self.height = h
        self.x = [0]*h
        self.y = [0]*h
        self.code = [0]*h
        pass


def decode_sprite(offset):
    info = sprite_info.get(offset,dict())
    sprite_name = info.get("name","unknown")

    nb_blocks = prog[offset+1]
    block_size = 8

    result = prog[offset:offset+nb_blocks*block_size+2]

    blocks = result[2:]



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
                FUCK


        for x in range(w):

            # maybe, birdie try appears to specify the base code for each part..
            code = spriteram[offs + 1] & 0x1fff

            code &= ~(h - 1)

            # not affected by flipscreen
            if (parentFlipY): # in the case of multi-width sprites the y flip bit is set by the parent
                incy = -1
            else:

                code += h - 1
                incy = 1


            sprite_ptr = SpritePtr(h)
            if True: # (not flash or (screen.frame_number() & 1))


                sprite_ptr.colour = colour;
                sprite_ptr.flipx = flipx;
                sprite_ptr.flipy = flipy;
                if (priority):

                    sprite_ptr.pri_mask = pri_mask
                    for y in range(h):

                        sprite_ptr.code[y] = code - y * incy
                        sprite_ptr.x[y] = sx + (mult * x)
                        sprite_ptr.y[y] = sy + (mult * y)

                    spritelist.append(sprite_ptr)

                else:

                    for y in range(h):

                        sprite_ptr.code[y] = code - y * incy
                        sprite_ptr.x[y] = sx + (mult * x)
                        sprite_ptr.y[y] = sy + (mult * y)

                    sprite_objects.append(sprite_ptr)
    ##                            gfx(0)->transpen(bitmap, cliprect,
    ##                                sprite_ptr->code[y],
    ##                                sprite_ptr->colour,
    ##                                sprite_ptr->flipx, sprite_ptr->flipy,
    ##                                sprite_ptr->x[y], sprite_ptr->y[y], 0);





    ##    if priority!
    ##    {
    ##        while (sprite_ptr != m_spritelist.get())
    ##        {
    ##            sprite_ptr--;
    ##
    ##            for (int y = 0; y < sprite_ptr->height; y++)
    ##            {
    ##                gfx(0)->prio_transpen(bitmap, cliprect,
    ##                        sprite_ptr->code[y],
    ##                        sprite_ptr->colour,
    ##                        sprite_ptr->flipx, sprite_ptr->flipy,
    ##                        sprite_ptr->x[y], sprite_ptr->y[y], screen.priority(), sprite_ptr->pri_mask, 0);
    ##            };
    ##        }



    sprite_image = Image.new("RGB",(128,128))

    for so in sprite_objects:
        for i in range(so.height):
            img = tiles[so.code[i]]
            x = so.x[i]
            y = so.y[i]
            if y > 128:
                y -= 256
            if x > 128:
                x -= 256
            print(hex(so.code[i]),x,y)

            x += 60
            y += 60

            sprite_image.paste(img,(x,y))

    sprite_image = ImageOps.scale(sprite_image,5,resample=Image.Resampling.NEAREST)

    sprite_image.save(f"dumps/{sprite_name}_{offset:x}.png")


for offset in assembled_sprites:
    decode_sprite(offset)

#decode_sprite(0x52f8a)
