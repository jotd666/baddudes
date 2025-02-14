from PIL import Image,ImageOps
import os,sys,bitplanelib,json,pathlib

from shared import *

dump_subdir = dump_dir / "front_objects"


def gen_data_file(asm_out,fo_bin,palette,objects):
    with open(asm_out,"w") as f:
        f.write("palette:\n")
        bitplanelib.palette_dump(palette,f)
        f.write(f"\tdc.w\t{len(objects)}\t; number of front objects\n; display Y\n")
        for k,o in objects.items():
            y = 240-o.size[1]
            f.write(f"\tdc.w\t{y}\n")
        f.write("main_table:\n")
        for k,o, in objects.items():
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

def doit_level_1(dump_it=False):
    asm_out = generated_src_dir / "front_objects_1.68k"
    fo_bin = data_dir / "front_objects_1.bin"

    img = Image.open(whole_pics_dir / "front_objects_1.png")
    img = img.quantize(16,dither=0)

    palette = bitplanelib.palette_extract(img)
    transparent_first(palette,transparent)

    meter = Image.new("RGB",(64,48))  # 16 is enough
    meter.paste(img,(-56,-176))
    lamp_1 = Image.new("RGB",(64,184))   # 16 is enough
    lamp_1.paste(img,(-376,-40))
    lamp_2 = Image.new("RGB",lamp_1.size)
    lamp_2.paste(img,(-628,-40))
    hydrant = Image.new("RGB",(64,32))   # 16 is enough
    hydrant.paste(img,(-952,-192))

    objects = {"meter":meter,"lamp_1":lamp_1,"lamp_2":lamp_2,"hydrant":hydrant}

    if dump_it:
        ensure_exists(dump_subdir)
        img.save(dump_subdir / "front_objects_1_16.png")
        meter.save(dump_subdir / "meter.png")
        lamp_1.save(dump_subdir / "lamp_1.png")
        lamp_2.save(dump_subdir / "lamp_2.png")
        hydrant.save(dump_subdir / "hydrant.png")

    gen_data_file(asm_out,fo_bin,palette,objects)

def doit_level_2(dump_it=False):
    # level 2
    asm_out = generated_src_dir / "front_objects_2.68k"
    fo_bin = data_dir / "front_objects_2.bin"

    img = Image.open(whole_pics_dir / "front_objects_2.png")
    #img = img.quantize(16,dither=0)
    palette = bitplanelib.palette_extract(img)
    transparent_first(palette,transparent)
    palette_pad(palette,16)

    lamp_1 = Image.new("RGB",(64,184))   # 16 is enough
    lamp_1.paste(img,(-96-8,-40))

    objects = {"lamp_3":lamp_1}

    if dump_it:
        ensure_exists(dump_subdir)
        lamp_1.save(dump_subdir / "lamp_3.png")

    gen_data_file(asm_out,fo_bin,palette,objects)

if __name__ == "__main__":

    doit_level_1(True)
    doit_level_2(True)
