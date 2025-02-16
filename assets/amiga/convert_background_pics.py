from PIL import Image,ImageOps
import os,sys,bitplanelib,subprocess,json,pathlib

from shared import *

empty_plane_workaround = True


forest_replacement_dict = {(34,17,0):(17,34,0),
(56,34,1):(17,56,0),
(71,56,17):(71,90,0),
(90,71,34):(56,71,0)}

def doit(name,transparent_pix_coord,replacement_dict=None):
    asm_out = generated_src_dir / f"{name}.68k"
    dudes_bin = data_dir / f"{name}.bin"


    img = Image.open(whole_pics_dir / f"{name}.png")

    y_max = 240
    img=img.crop((0,0,256,y_max))

    # lose the black for transparent, background is black anyway (saves 1 color)
    bitplanelib.replace_color(img,{(0,0,0)},transparent)
    # if specified, change some colors before quantizing
    if replacement_dict:
        bitplanelib.replace_color_from_dict(img,replacement_dict)

    img_sprite = img.quantize(colors=4,dither=0).convert('RGB')

    changed_transparent = img.getpixel(transparent_pix_coord)   # where to find a transparent color
    bitplanelib.replace_color(img_sprite,{changed_transparent},img.getpixel(transparent_pix_coord))


    # cut in 4 64-pixel wide pics
    strips = []
    for i in range(4):
        strip = Image.new("RGB",(64,y_max))
        strip.paste(img_sprite,(-i*64,0))
        #strip.save(dump_dir/f"{name}_{i}.png")
        strips.append(strip)


    palette = bitplanelib.palette_extract(img_sprite)
    transparent_first(palette,transparent)
    with open(asm_out,"w") as f:
        f.write("main_table:\n")
        # make it suitable for 6 plane display
        for j in range(4):
            f.write(f"\tdc.l    strip_{j}-main_table        ; sprite start control word\n")
            f.write(f"\tdc.l    strip_{j}_end-main_table-16        ; sprite end control word\n")  # end control word position
        f.write("; 4 color palette\n")
        bitplanelib.palette_dump(palette,f)
        for j,img in enumerate(strips):
            f.write(f"strip_{j}:\n")
            sdata = bitplanelib.palette_image2sprite(img,None,palette,sprite_fmode=3)
            bitplanelib.dump_asm_bytes(sdata,f)
            f.write(f"strip_{j}_end:\n")

    asm2bin(asm_out,dudes_bin)


def doit_forest():
    doit("forest",(0,140),forest_replacement_dict)
def doit_cave():
    doit("cave",(0,140))

if __name__ == "__main__":
    doit_forest()
    doit_cave()

