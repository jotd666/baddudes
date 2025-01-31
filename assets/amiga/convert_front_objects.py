from PIL import Image,ImageOps
import os,sys,bitplanelib,json,pathlib

from shared import *


def doit(force=False):
    asm_out = generated_src_dir / "front_objects_1.68k"
    fo_bin = data_dir / "front_objects_1.bin"
    if force or not dudes_bin.exists():
        img = Image.open(whole_pics_dir / "front_objects_1.png")
        img = img.quantize(16,dither=0)

        palette = bitplanelib.palette_extract(img)
        transparent_first(palette,transparent)

        meter = Image.new("RGB",(64,48))  # 16 is enough
        meter.paste(img,(-56,-176))
        lamp_1 = Image.new("RGB",(64,160))   # 16 is enough
        lamp_1.paste(img,(-376,-40))
        lamp_2 = Image.new("RGB",lamp_1.size)
        lamp_2.paste(img,(-628,-40))
        hydrant = Image.new("RGB",(64,32))   # 16 is enough
        hydrant.paste(img,(-952,-192))

        objects = {"meter":meter,"lamp_1":lamp_1,"lamp_2":lamp_2,"hydrant":hydrant}

        if True:
            img.save("front_objects_16.png")
            meter.save("meter.png")
            lamp_1.save("lamp_1.png")
            lamp_2.save("lamp_2.png")
            hydrant.save("hydrant.png")

        with open(asm_out,"w") as f:
            f.write("palette:\n")
            bitplanelib.palette_dump(palette,f)
            f.write("\tdc.w\t4\t; number of front objects\n")
            f.write("main_table:\n")
            for k,o in objects.items():
                for j in range(2):
                    f.write(f"\tdc.l\tobject_{k}_{j}-main_table\n")

            for k,o in objects.items():
                outs = bitplanelib.palette_image2attached_sprites(o,None,palette,sprite_fmode=3)
                cw_offset = len(outs[0])-16
                for j,out in enumerate(outs):
                    f.write(f"""\tdc.w\t${cw_offset:04x}  ; offset of end control word for next object
\tCNOP\t0,8     ; align on 8 bytes else sprite is not properly displayed
\tdc.w 0,0,0    ; keep this alignment
\tdc.w\t{o.size[1]}   ; sprite height
object_{k}_{j}:""")

                    bitplanelib.dump_asm_bytes(out,f)

        asm2bin(asm_out,fo_bin)


if __name__ == "__main__":

    doit(force=True)
