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
# 4) keep track of the processed pixel to be able to perform a second pass with a possible different fake black

this_dir = pathlib.Path(__file__).absolute().parent

transparent_color = (255,0,255)
black_color = (0,0,0)

def gray(c):
    return (c,)*3

def fix_black(pic_name,shadow_pic_name,fake_black,processed_pixels):
    pic = PIL.Image.open(shadow_pic_name)
    # extract X,Y where pixels are supposed to be black
    really_black_coords = {(x,y) for x in range(pic.size[0]) for y in range(pic.size[1]) if pic.getpixel((x,y)) == fake_black}

    processed_pixels = processed_pixels.copy()

    pic = PIL.Image.open(pic_name)
    for x in range(pic.size[0]):
        for y in range(pic.size[1]):
            # convert all black to transparent
            if (x,y) not in processed_pixels and pic.getpixel((x,y)) == black_color:
                pic.putpixel((x,y),transparent_color)
            # if it's an actual black color (revealed by another pic of the set
            # with a possible bogus palette), restore it
            if (x,y) in really_black_coords:
                pic.putpixel((x,y),black_color)
                processed_pixels.add((x,y))

    return pic,processed_pixels

def fix_tileset(name,target_palette,black_reveal_palette_index,fake_black,processed_pixels=set()):

    tiles_dir = this_dir /"sheets"/f"{name}_black"
    tiles_out_dir = this_dir /"sheets"/name


    if target_palette==black_reveal_palette_index:
        raise Exception("target & reveal palette can't be identical")

    shadow_pic_name = f"pal_{black_reveal_palette_index:02x}.png"
    pic_name = f"pal_{target_palette:02x}.png"

    pic,processed_pixels = fix_black(tiles_dir / pic_name,tiles_dir / shadow_pic_name,fake_black,processed_pixels)

    out_pic_name = tiles_out_dir / pic_name
    print(f"Saving {out_pic_name}")
    pic.save(out_pic_name)

    return processed_pixels


if True:
    # it's too hard to dynamically change boss 4 palette with quantization
    # better insert the proper colors
    boss_4_source = this_dir /"sheets"/"misc"/"boss_4_0F.png"
    img = PIL.Image.open(boss_4_source)
    boss4 = img.crop((0,608,1024,656))
    sprites_black_0F = this_dir /"sheets"/"sprites_black"/"pal_0F.png"
    img2 = PIL.Image.open(sprites_black_0F)
    img2.paste(boss4,(0,608))
    # overwrite black pic
    img2.save(sprites_black_0F)

    # same thing for mutant karnov
    karnov_9_source = this_dir /"sheets"/"misc"/"karnov_09.png"
    img = PIL.Image.open(karnov_9_source)
    boss4 = img.crop((0,256,1024,256+16*3))
    sprites_black_09 = this_dir /"sheets"/"sprites_black"/"pal_09.png"
    img2 = PIL.Image.open(sprites_black_09)
    img2.paste(boss4,(0,256))
    y = 480
    boss4 = img.crop((0,y,1024,y+16))
    img2.paste(boss4,(0,y))
    # overwrite black pic
    img2.save(sprites_black_09)

    # simpler too... for elevator doors (level 7)
    karnov_9_source = this_dir /"sheets"/"misc"/"elevator_0E.png"
    img = PIL.Image.open(karnov_9_source)
    sprites_black_09 = this_dir /"sheets"/"sprites_black"/"pal_0E.png"
    img2 = PIL.Image.open(sprites_black_09)
    y = 672
    boss4 = img.crop((0,y,1024,y+16))
    img2.paste(boss4,(0,y))
    # overwrite black pic
    img2.save(sprites_black_09)

    fix_tileset("sprites",0x4,0x9,gray(71))   # red ninja girl
    fix_tileset("sprites",0x3,0x9,gray(71))   # gray ninja
    fix_tileset("tiles_244000",0,4,(159,90,56))
    fix_tileset("sprites",0,0xA,gray(195))   # player tiles
    fix_tileset("sprites",2,0x9,gray(71))   # ninja tiles

    # chain 2 fixes from 2 different fake black sources, we have to remember which pixels
    # have been processed, else the second processing destroys the black pixels of the first one!
    processed_pixels = fix_tileset("sprites",0xF,0xD,(56,34,1))   # karnov tiles
    fix_tileset("sprites",0xF,0x9,gray(104),processed_pixels)   # animal tiles

    fix_tileset("sprites",0xB,0x7,(230,230,0))   # car tires

    # chain 2 fixes from 2 different fake black sources, we have to remember which pixels
    # have been processed, else the second processing destroys the black pixels of the first one!
    processed_pixels = fix_tileset("sprites",0x9,0xD,(56,34,1))   # karnov 2
    fix_tileset("sprites",0x9,0x7,(230,230,0),processed_pixels)   # truck tires
    fix_tileset("sprites",0xA,0x7,(230,230,0))   # cars
    fix_tileset("sprites",0xC,0x7,(230,230,0))   # cars
    fix_tileset("sprites",0x5,0xD,(56,34,1))   # ninja nails
    fix_tileset("sprites",0xE,0xD,(56,34,1))   # elevator

    for i in range(0,2):
        fix_tileset("ending_sprites",i,0x4,(104,71,0))
    fix_tileset("ending_sprites",0x2,0x3,(0,0,56))
