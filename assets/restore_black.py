import PIL.Image,pathlib

this_dir = pathlib.Path(__file__).absolute().parent

tiles_dir = this_dir /"sheets"/"tiles_244000"

transparent_color = (255,0,255)
black_color = (0,0,0)

shadow_pic = "pal_04.png"

pic = PIL.Image.open(tiles_dir / shadow_pic)

outline_coords = {(x,y) for x in range(pic.size[0]) for y in range(pic.size[1]) if pic.getpixel((x,y)) == (159,90,56)}

for img in tiles_dir.iterdir():
    if img.name != shadow_pic:
        pic = PIL.Image.open(img)
        out_pic_name = tiles_dir.parent / img.name
        for x in range(pic.size[0]):
            for y in range(pic.size[1]):
                if pic.getpixel((x,y)) == black_color:
                    pic.putpixel((x,y),transparent_color)
                if (x,y) in outline_coords:
                    pic.putpixel((x,y),black_color)
        pic.save(out_pic_name)