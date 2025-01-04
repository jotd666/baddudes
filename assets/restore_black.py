import PIL.Image,pathlib

# MAME tile saving edition is a precious asset when it comes to ripping the graphics.
# the only issue with that tool is that it dumps transparent color as black, so where there
# is real black in pic, the data is lost. A way to workaround this is to find one of the tile sheet
# where background black is not drawing black. Here it's tile palette 04, where black outline is brown.
#
# 1) store black outline color coords from tiles palette 4
# 2) for other tile sheets, convert black to magenta (tranparent)
# 3) apply black on stored coords

this_dir = pathlib.Path(__file__).absolute().parent

def fix_tileset(name,black_reveal_palette_index):

    tiles_dir = this_dir /"sheets"/f"{name}_black"
    tiles_out_dir = this_dir /"sheets"/name

    transparent_color = (255,0,255)
    black_color = (0,0,0)

    shadow_pic = f"pal_{black_reveal_palette_index:02x}.png"

    pic = PIL.Image.open(tiles_dir / shadow_pic)

    outline_coords = {(x,y) for x in range(pic.size[0]) for y in range(pic.size[1]) if pic.getpixel((x,y)) == (159,90,56)}

    for img in tiles_dir.iterdir():
        pic = PIL.Image.open(img)
        out_pic_name = tiles_out_dir / img.name
        for x in range(pic.size[0]):
            for y in range(pic.size[1]):
                if pic.getpixel((x,y)) == black_color:
                    pic.putpixel((x,y),transparent_color)
                if (x,y) in outline_coords:
                    pic.putpixel((x,y),black_color)
        pic.save(out_pic_name)

fix_tileset("tiles_244000",4)
fix_tileset("sprites",0)
