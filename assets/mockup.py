from PIL import Image,ImageOps
import os

# to dump tiles+sprites memory in MAME:
#save title,$240000,$31c800-$240000

name_template = "gfx dev {dev} set {set} tiles 16x16 colors 16 pal {pal:02x}.png"

this_dir = os.path.dirname(os.path.abspath(__file__))

tilesdir = os.path.join(this_dir,os.pardir,"mame","baddudes")

with open(os.path.join(this_dir,"title"),"rb") as f:
    contents = f.read()

tiles_06 = name_template.format(dev=0,set=1,pal=6)

side = 16
transparent = (254,254,254)  # not possible to get it in the game

blank_image = Image.new("RGB",(side,side))
for i in range(side):
    for j in range(side):
        blank_image.putpixel((i,j),transparent)


def load_tileset(image_name,side,dump_prefix=""):
    full_image_path = os.path.join(tilesdir,image_name)
    tiles_1 = Image.open(full_image_path)
    nb_rows = tiles_1.size[1] // side
    nb_cols = tiles_1.size[0] // side

    dumpdir = "dumps"

    tileset_1 = []
    k=0
    for j in range(nb_rows):
        for i in range(nb_cols):
            img = Image.new("RGBA",(side,side))
            img.paste(tiles_1,(-i*side,-j*side))
            tileset_1.append(img)
##            if dump_prefix:
##                img = ImageOps.scale(img,5,resample=Image.Resampling.NEAREST)
##                img.save(os.path.join(dumpdir,f"{dump_prefix}_{k:02x}.png"))
            k += 1

    return tileset_1

def create_layer(tileset,address):
    used_tiles = set()
    layer_nb_rows = 34
    layer_nb_cols = 32
    layer_1 = Image.new("RGBA",(layer_nb_rows*side,layer_nb_cols*side))

    current_x = 0
    current_y = 0
    for addr in range(address,address+0x800,2):
        c1 = contents[addr]
        c2 = contents[addr+1]
        c = ((c1&0xF)<<8)+c2
        attr = c1 >> 4


        if c < 2048:
            used_tiles.add(c)
            img = tileset[c]
            layer_1.paste(img,(current_x,current_y))

        current_x += side
        if current_x == layer_nb_cols*side:
            current_x = 0
            current_y += side
    return used_tiles,layer_1



ts_title = load_tileset(tiles_06,16)
used_tiles,layer = create_layer(ts_title,0xA000)

layer.save("title.png")

if False:
    game_layer = []
    used_tiles = []
    for i in range(0,3):
        tileset = load_tileset(f"tiles_{i}.png",True,side)
        ut,layer = create_layer(tileset,0xC400+(0x400*i))
        game_layer.append(layer)
        used_tiles.append(ut)
        layer.save(f"game_layer_{i+1}.png")


    all_layers = Image.new("RGBA",layer.size)

    layer = game_layer[2]
    all_layers.paste(layer,(0,0),layer)
    layer = game_layer[1]
    all_layers.paste(layer,(0,0),layer)
    layer = game_layer[0]
    all_layers.paste(layer,(0,-16),layer)

    # sprites at D100
    # X,Y,attribute (0,1 X flip) and code starting from 0x40

    sprites_set = load_tileset("sprites_4.png",True,16,"sprite")

##    for sprite_address in range(0xD100,0xD200,4):
##        block = contents[sprite_address-0x8000:sprite_address-0x8000+4]
##        x,y,attribute,code = block
##
##        code -= 0x40
##        y = 240-y
##        sprite = sprites_set[code]
##
##        all_layers.paste(sprite,(x,y))


##    all_layers.save("in_game_layers.png")

