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
            if y == 223:
                y = -33
            print(hex(so.code[i]),x,y)

            x += 60
            y += 60

            sprite_image.paste(img,(x,y))

    sprite_image = ImageOps.scale(sprite_image,5,resample=Image.Resampling.NEAREST)

    sprite_image.save(f"dumps/image_{offset:x}.png")


for offset in assembled_sprites:
    decode_sprite(offset)