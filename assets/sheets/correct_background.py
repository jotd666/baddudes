# the palette hack allowed to turn foreground blacks to purple, now
# we invert to get purple in the back, blacks where they were

from PIL import Image
import pathlib
black=(0,0,0)
magenta=(255,0,255)
magenta4=(240,0,240)

def change(input_img,output_img):
    img = Image.open(input_img)
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            c = img.getpixel((x,y))
            if c==black:
                c = magenta
            elif c==magenta4:
                c = black
            img.putpixel((x,y),c)


    img.save(output_img)

##sprites_out = pathlib.Path("sprites")
##sprites_out.mkdir(exist_ok=True)
##for i in range(16):
##    pname = f"pal_{i:02x}.png"
##    input_img = pathlib.Path("sprites_mag") / pname
##    output_img = sprites_out / pname

change("gfx dev 1 set 0 tiles 16x16 colors 16 pal 09.png","pal_09_new.png")