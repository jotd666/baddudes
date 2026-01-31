# hacks a saved palette of the game
# and injects magenta on black colors (but not on background colors)
# so MAME gfxsave generates pngs with magenta instead of black: invert those
# colors and we get magenta as background
#
# this technique was used in Ghosts'n'Goblins first and seems to be so much better
# on that game that the old "find a non-black in a clut somewhere" hack which misses
# and fails for some palettes depending on the level
#
# so how the proper tiles are generated for sprites?
#
# first dump palette with mame: save palette,$310000,$4800
# then run this script on the saved input, this generates "magenta_palette"
# now load in mame again: load magenta_palette,$310000
#
# at this point, all character black colors turn to magenta. Check with F4 that the backgrounds
# remain black. Dump sheets (F12 in mame gfxsave)
# then turn black to magenta and magenta (rgb4) to black => the sheets are clean

with open("palette","rb") as f:
    contents = bytearray(f.read())

# first part at 310000, then at 314000
first_part = contents[0:0x800]
second_part = contents[0x4000:0x4800]

for i in range(0,len(first_part)-1,2):
    rg = first_part[i]*256+first_part[i+1]
    b = second_part[i]*256+second_part[i+1]
    if rg == b == 0 and i%0x10:   # real background black is on 0x10 aligned
        print(hex(i))
        #first_part[i] = 0xF0
        first_part[i+1] = 0xF0
        second_part[i+1] = 0xF0

with open("magenta_palette","wb") as f:
    f.write(first_part)
    f.write(bytes(0x3800))
    f.write(second_part)