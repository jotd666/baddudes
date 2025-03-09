import os,json,pathlib,struct
import bitplanelib

this_dir = pathlib.Path(__file__).absolute().parent

def doit(filename):
    print(">>>>>>>> ",filename)
    with open(filename,"rb") as f:
        sprite_ram = f.read()

    with open(os.path.join(this_dir,"sprite_code_names.json"),"r") as f:
        sprite_name_code = {int(k,16):v for k,v in json.load(f)["codes_names"].items()}

    for i in range(0,len(sprite_ram),8):
        block = sprite_ram[i:i+8]
        y,code,x,_ = struct.unpack_from(">HHHH",block)
        if y & 0x8000 != 0:
            attrs = y & 0xFE00
            x &= 0x1FF
            y &= 0x1FF
##            if x >= 256:
##                x -= 0x200
##            if y >= 256:
##                y -= 0x200
            x = 240 - x
            y = 240 - y
            y_flip = attrs & 0x4000
            x_flip = attrs & 0x2000

            name = sprite_name_code.get(code,"unknown")
            print(f"address={i+0xFFC000:06x}, x={x}, y={y}, code={code:x}, attrs={attrs:x}, name={name}")

    with open(filename+".68k","w") as f:
        bitplanelib.dump_asm_bytes(sprite_ram,f,mit_format=True)

doit("boss_6_bug")
