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

tiles_dir = this_dir /"sheets"/"tiles_244000_black"
tiles_out_dir = this_dir /"sheets"/"tiles_244000"

transparent_color = (255,0,255)
black_color = (0,0,0)

shadow_pic = "pal_04.png"

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