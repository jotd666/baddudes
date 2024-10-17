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

data ="""
    dc.w    $0506    ;53c0e

    dc.w    $80e1    ;53c10
    dc.w    $020c    ;53c12
    dc.w    $00fc    ;53c14
    dc.w    $0000    ;53c16

    dc.w    $88f1    ;53c18
    dc.w    $0208    ;53c1a
    dc.w    $00fc    ;53c1c
    dc.w    $0000    ;53c1e

    dc.w    $8011    ;53c20
    dc.w    $0200    ;53c22
    dc.w    $00fc    ;53c24
    dc.w    $0000    ;53c26

    dc.w    $80e1    ;53c28
    dc.w    $020d    ;53c2a
    dc.w    $00ec    ;53c2c
    dc.w    $0000    ;53c2e

    dc.w    $88f1    ;53c30
    dc.w    $020a    ;53c32
    dc.w    $00ec    ;53c34
    dc.w    $0000    ;53c36

    dc.w    $8011    ;53c38
    dc.w    $0201    ;53c3a
    dc.w    $00ec    ;53c3c
    dc.w    $0000    ;53c3e
"""

result = []
for line in data.splitlines():
    toks = line.split()
    if len(toks)>1 and toks[0]=="dc.w":
        word = int(toks[1].strip("$"),16)
        result.append(word>>8)
        result.append(word&0xFF)

result = bytearray(result)

dev = 1
st = 0
pal = 2

blue_ninja_tiles = Image.open(os.path.join(tilesdir,name_template.format(dev=dev,st=st,pal=pal)))

tiles = load_tileset(blue_ninja_tiles,16,"ninjas","dumps")

nb_blocks = result[1]
block_size = 8

sprite_image = Image.new("RGB",(32,64))

blocks = result[2:]


class SpritePtr:
    def __init__(self,h):
        self.height = h
        self.x = [0]*h
        self.y = [0]*h
        self.code = [0]*h
        pass

for idx,i in enumerate(range(0,block_size*nb_blocks,block_size)):
    offs = 0
    pri_mask = 0
    block = blocks[i:i+block_size]
    spriteram = [(b[i+j]<<8)+b[i+j+1] for j in range(0,block_size,2)]

    spritelist = []

    data0 = spriteram[offs];
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

    if (m_flip_screen):

            sy = 240 - sy;
            sx = 240 - sx;
            flipx = not flipx
            flipy = not flipy
            mult = 16

        else:
            mult = -16

        if (!(spriteram[offs] & 0x8000)):
        {
            offs += 4
            FUCK
        }

        for x in range(w):

            if (offs < size):

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


    h = (1 << ((data0 & 0x1800) >> 11))   # 1x, 2x, 4x, 8x height */
    w = (1 << ((data0 & 0x0600) >>  9))   # 1x, 2x, 4x, 8x width */
    img = tiles[tile]
    print(hex(tile),h,w)
    yo = data0 & 0xFF
    if yo==0x11:
        y = 0
    elif yo==0xE1:
        y = 32
    else:
        y = 16

    x = 4
    if data2 == 0xEC:
        x += 16

    sprite_image.paste(img,(x,y))

sprite_image = ImageOps.scale(sprite_image,5,resample=Image.Resampling.NEAREST)

sprite_image.save("ninja.png")