from PIL import Image
import bitplanelib

img1 = Image.open("baddudes_level_2_start/pal 0F.png")

img2 = Image.open("baddudes_level_2_end/pal 0F.png")

d = {}
for x in range(img1.size[0]):
    for y in range(img1.size[1]):
        p1 = img1.getpixel((x,y))
        p2 = img2.getpixel((x,y))
        if p1 != p2:
            d[p1] = p2

for k,v in d.items():
    print("\t.word\t{},{}".format(hex(bitplanelib.to_rgb4_color(k)),hex(bitplanelib.to_rgb4_color(v))))

