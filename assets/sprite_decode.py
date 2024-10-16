from PIL import Image,ImageOps
import os

#dev 1 set 0: sprites:
#pal 0: player 1, white ninja
#pal 1: player 2, green ninja
#pal 2: blue ninjas
#pal 3: gray ninjas
#pal F: red ninjas

name_template = "gfx dev {dev} set {st} tiles 16x16 colors 16 pal {pal:02x}.png"

this_dir = os.path.dirname(os.path.abspath(__file__))

tilesdir = os.path.join(this_dir,os.pardir,"mame","baddudes")

data ="""
    dc.w    $0506    ;53c0e
    dc.w    $80e1    ;53c10
    dc.w    $020c    ;53c12
    dc.w    $00fc    ;53c14
    dc.w    $0000    ;53c16
    dc.w    $88f1    ;53c18
    dc.w    $0208    ;53c1a
    dc.w    $00fc    ;53c1c
    dc.w    $0000    ;53c1e
    dc.w    $8011    ;53c20
    dc.w    $0200    ;53c22
    dc.w    $00fc    ;53c24
    dc.w    $0000    ;53c26
    dc.w    $80e1    ;53c28
    dc.w    $020d    ;53c2a
    dc.w    $00ec    ;53c2c
    dc.w    $0000    ;53c2e
    dc.w    $88f1    ;53c30
    dc.w    $020a    ;53c32
    dc.w    $00ec    ;53c34
    dc.w    $0000    ;53c36
    dc.w    $8011    ;53c38
    dc.w    $0201    ;53c3a
    dc.w    $00ec    ;53c3c
    dc.w    $0000    ;53c3e
"""

result = []
for line in data.splitlines():
    toks = line.split()
    if len(toks)>1 and toks[0]=="dc.w":
        word = int(toks[1].strip("$"),16)
        result.append(word>>8)
        result.append(word&0xFF)

result = bytearray(result)

dev = 1
st = 0
pal = 2

blue_ninja_tiles = Image.open(os.path.join(tilesdir,name_template.format(dev=dev,st=st,pal=pal)))
