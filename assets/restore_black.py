import PIL.Image,pathlib

# MAME tile saving edition is a precious asset when it comes to ripping the graphics.
# the only issue with that tool is that it dumps transparent color as black, so where there
# is real black in pic, the data is lost. A way to workaround this is to find one of the tile sheet
# where background black is not drawing black. Here it's tile palette 04/0A, where black outline is brown/
# black colors of the dudes sneakers is gray
#
# 1) store black (fake black) color coords from tiles palette xx where black is differentiated from background
# (and called "fake black" here
# 2) for other tile sheets, convert black to magenta (tranparent)
# 3) apply black on stored coords

this_dir = pathlib.Path(__file__).absolute().parent

def gray(c):
    return (c,)*3

def fix_tileset(name,target_palette,black_reveal_palette_index,fake_black):

    tiles_dir = this_dir /"sheets"/f"{name}_black"
    tiles_out_dir = this_dir /"sheets"/name

    transparent_color = (255,0,255)
    black_color = (0,0,0)

    if target_palette==black_reveal_palette_index:
        raise Exception("target & reveal palette can't be identical")

    shadow_pic = f"pal_{black_reveal_palette_index:02x}.png"

    pic = PIL.Image.open(tiles_dir / shadow_pic)

    # extract X,Y where pixels are supposed to be black
    really_black_coords = {(x,y) for x in range(pic.size[0]) for y in range(pic.size[1]) if pic.getpixel((x,y)) == fake_black}

    img = tiles_dir / f"pal_{target_palette:02x}.png"

    pic = PIL.Image.open(img)
    out_pic_name = tiles_out_dir / img.name
    for x in range(pic.size[0]):
        for y in range(pic.size[1]):
            # convert all black to transparent
            if pic.getpixel((x,y)) == black_color:
                pic.putpixel((x,y),transparent_color)
            # if it's an actual black color (revealed by another pic of the set
            # with a possible bogus palette), restore it
            if (x,y) in really_black_coords:
                pic.putpixel((x,y),black_color)
    print(f"Saving {out_pic_name}")
    pic.save(out_pic_name)

fix_tileset("tiles_244000",0,4,(159,90,56))
fix_tileset("sprites",0,0xA,gray(195))   # player tiles
fix_tileset("sprites",2,0x9,gray(71))   # ninja tiles
