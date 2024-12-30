import os,pathlib,re
import ira_asm_tools

this_dir = pathlib.Path(os.path.abspath(__file__)).parent
src_dir = this_dir / os.pardir / "src"

asmfile = r"K:\jff\AmigaHD\PROJETS\GameRelocs\BadDudes\bad_dudes.s"

af = ira_asm_tools.AsmFile(asmfile)

relocated_ram_offsets = {}

def is_in_ram(ext_address):
    return 0xff8000 <= ext_address <= 0x00ffc000

special_read = {0x300000,0x300001,0x300008,0x300009} | set(range(0x30c000, 0x30c010))

manual_patch_declare = dict()

patchlist = {}
patch_functions = {}
to_be_manually_patched = {}

def add_i(offset,comment=""):
    patchlist[offset] = {"type":"I","comment":comment}

def add_r(offset,comment=""):
    patchlist[offset] = {"type":"R","comment":comment}

def add_b(offset,value,comment=""):
    patchlist[offset] = {"type":"B","comment":comment,"value":str(value)}

def add_nop(offset,count,comment=""):
    patchlist[offset] = {"type":"NOP","value":str(count),"comment":comment}

def add_p(offset,patch_function=None,comment=""):
    if patch_function is None:
        # deduce the offset from patch function suffix (which contains hex address)
        patch_function = offset
        offset = int(offset.split("_")[-1],0x10)
    patchlist[offset] = {"type":"P","value":patch_function,"comment":comment}

def add_ps(offset,patch_function=None,comment=""):
    add_pss(offset,patch_function,0,comment)

def add_pss(offset,patch_function=None,fill=0,comment=""):

    if patch_function is None:
        # deduce the offset from patch function suffix (which contains hex address)
        patch_function = offset
        offset = int(offset.split("_")[-1],0x10)

    if fill==0:
        patchlist[offset] = {"type":"PS","value":patch_function,"comment":comment}
    else:
        patchlist[offset] = {"type":"PSS","value":patch_function,"fill":fill,"comment":comment}

def add_s(offset,jump_to,comment=""):
    patchlist[offset] = {"type":"S","value":f"0x{jump_to:04x}-0x{offset:04x}-2","comment":comment}

def add_nop(offset,fill,comment=""):
    patchlist[offset] = {"type":"NOP","fill":fill,"comment":comment}



for line in af.lines:
    inst_info = ira_asm_tools.parse_instruction_line(line)

    if inst_info:
        args = inst_info["arguments"]
        # generate offsets to relocate RAM
        if inst_info["size"] in [4,6,8,10]:
            for i,arg in enumerate(args):

                if inst_info["instruction"].lower().startswith("dc."):
                    offset = 0
                else:
                    offset = 2 if i==0 else inst_info["size"]-4
                prefix,*rest = arg.split("_")
                if rest:
                    try:
                        ext_address = int(rest[-1],16)
                        reloc_address = inst_info["address"]

                        if is_in_ram(ext_address):
                            # in RAM: relocate

                            relocated_ram_offsets[(reloc_address,offset)] = arg
                        elif ext_address >= 0x240000:
                            instruction = inst_info["instruction"]
                            if instruction.startswith(("MOVE.","ADD.","SUB.")):
                                size = instruction[-1]
                                size = {"W":2,"B":1,"L":4}[size]

                                size_str = {2:"word",1:"byte",4:"long"}[size]
                                operation = None
                                # laying out 4 traps for read/write byte/word
                                if i==0:
                                    # read
                                    if ext_address in special_read:
                                        src = ext_address
                                        src_str = f"{src:08x}"
                                        dest = args[1]
                                        dest_str = dest.strip("$")
                                        operation = "read"
                                else:
                                    # write
                                    src = args[0]
                                    src_str = src.strip("#$")
                                    if "#" in src:
                                        src_str = "imm_"+src_str
                                    src = src.replace("$","0x")
                                    dest = ext_address
                                    dest_str = f"{dest:08x}"
                                    operation = "write"

                                if operation:
                                    patch_function = f"{operation}_{size_str}_{src_str}_to_{dest_str}"
                                    add_pss(reloc_address,patch_function,fill=inst_info["size"]-6)
                                    patch_functions[patch_function] = {"instruction":instruction.lower(),
                                    "operation":operation,"size":size,"src":src,"dest":dest,"size_str":size_str}
                            else:
                                to_be_manually_patched[inst_info["address"]] = inst_info


                    except ValueError:
                        pass

#############################################
# manual patches, may override auto patches #
#############################################

# note that passing a single string arg to add_ps or add_p assumes that
# the offset is the suffix: no need to repeat the patch address then

add_i(0x100,"spurious interrupt")
add_i(0x31c,"infinite loop")
add_r(0x003ee,"turn RTE to RTS in irq")
add_s(0x013e4,0x01422,"skip ram test")

add_ps(0xcd3e,"write_word_a0plus_to_0030c010","manual")
add_ps(0x01502,"clear_sound")
add_ps(0x0979a,"test_mcu_reply")
add_ps("copy_rom_to_video_1b310")
add_ps("enable_interrupts_01476")
add_s(0x0147c,0X0148e,"skip hw control stuff")
add_nop(0x01422,6,"set stack")
add_ps(0x01454,"set_palette_a2")
add_ps(0x0146a,"set_palette_a2")
add_r(0x097a4,"skipping some hardware init shit")
add_i(0x0166e,"reset")
add_p(0xe402,"videoram_write_loop_d1_d0")
add_p(0x01d5c,"videoram_write_loop_d1_d0")
add_p(0x01d70,"videoram_write_loop_d1_d0")
add_p(0x01d84,"videoram_write_loop_d1_d0")
add_p(0x01d98,"videoram_write_loop_d1_d0")
add_ps(0x01e16,"videoram_write_loop_d0_d1")
add_p(0x01e26,"videoram_write_loop_d0_d1")
add_ps(0x01daa,"videoram_write_loop_d0_d1")
add_p(0x01dba,"videoram_write_loop_d0_d1")
add_ps(0x01e00,"videoram_write_loop_d0_d1")
add_ps(0x001e52,"videoram_write_loop_d0_d1")
add_ps("videoram_write_062ae")
add_ps("videoram_write_062e2")
add_ps("videoram_write_loop_0e07e")
add_p("videoram_write_0e0ac")
add_p("videoram_write_01fca")
add_p("videoram_write_021e8")
add_p("videoram_clear_01ff8")
add_r(0x01dc2,"skip spriteram clear")  # temp
add_r(0x1e80)  # temp sprite attribute change
add_r(0x0979a,"mcu reply test")
add_p(0x372,"osd_enable_interrupts","mcu shit and enable interrupts")
add_r(0x14ee,"service mode test")
add_p("copy_to_palette_007be",comment="copy palette subroutine")
add_ps(0x01e68,"set_scroll_values","set column scroll")
add_ps(0x01e78,"set_scroll_values","set column scroll")
add_nop(0x01652,8)
add_b(0x0165a,0x60)
add_nop(0x0173C,8)
add_b(0x0173C+8,0x60)
add_p(0x00596,"osd_enable_interrupts")
add_p("copy_memory_to_tiles_0837c")
add_ps("copy_to_tile_064f6")
add_ps("write_ninja_message_0834A")
add_p("copy_to_tile_0_01fa2")
add_p("display_lives_0e122")
add_ps("write_to_tile_0_083ac")
add_ps("videoram_write_0e3ba")
add_pss("videoram_write_06c82",fill=0xC)
add_pss("write_to_tiles_0e30e",fill=4)
add_s(0x083ac+6,0x083c6)
add_s(0x003d0,0x003dc,"skip unneeded vblank wait")
add_ps("set_video_attribute_083ce")
add_s(0x083ce+6,0x083e8)
add_p("copy_highscore_tiles_loop_09592")
add_p("display_scores_loop_07b9a")
add_ps("set_game_context_1ab0")  # there are NOPs there
add_p("play_sound_0def0")
add_pss("copy_tiles_099f0",fill=4)
add_ps("videoram_write_08848")

for offset in [0x0174c,0x0175c,0x07e66]:
    add_pss(offset,"test_input_bit_d1",2)


for offset in [0x097ae,0x097b8,0x097c2]:
    add_pss(offset,"test_input_bit_7",2)


#############################################

auto_patch_declare = set(patchlist)
manual_patch_declare = {0x002c8,0x002de,0x020a6,0x020ba,0x02134,0x2148,0x07398,0x073d2,0x0740c,  # function write_tiles_of_given_color_01fc4 patched
}

to_be_manually_patched = {k:v for k,v in to_be_manually_patched.items() if k not in auto_patch_declare and k not in manual_patch_declare}

##nb_unpatched = 0
##for k,v in to_be_manually_patched.items():
##    if v["instruction"] not in ["dc.l"]:
##        nb_unpatched += 1
##        print(f";{k:05x}: {v}")
##
##print(f"\nunpatched: {nb_unpatched}")


with open(src_dir / "patchlist.68k","w") as f:
    f.write("""\t.macro\tSTORE_REGS
\tmove.w\td7,-(a7)
\tmove.l\ta6,-(a7)
\t.endm
\t.macro\tRESTORE_REGS
\tmove.l\t(a7)+,a6
\tmove.w\t(a7)+,d7
\t.endm

""")
    f.write("ram_relocs:\n")
    for (reloc,offset),v in sorted(relocated_ram_offsets.items()):
        f.write(f"\t.long\t0x{reloc:06x}+{offset}\t| {v}\n")
    f.write("\t.long\t-1\n")

    f.write("patchlist:\n\tPL_START\n")

    for offset,p in sorted(patchlist.items()):
        f.write("\tPL_{type}\t0x{offset:06x}".format(type=p["type"],offset=offset))
        value = p.get("value")
        if value is not None:
            f.write(f",{value}")
        fill = p.get("fill")
        if fill is not None:
            f.write(f",{fill}")
        comment = p.get("comment")
        if comment:
            f.write(f"\t| {comment}")
        f.write("\n")
    f.write("\tPL_END\n")

    f.write("\n")
    for k,v in sorted(patch_functions.items()):
        if not re.match("^\w+$",k):
            continue        # skip manually patched functions with (a0)+ shit in them and such

        f.write(f"{k}:\n\tSTORE_REGS\n")

        osd_call = "\n".format(**v)
        if v["operation"]=="read":
            # read operation
            f.write("""\tlea\t0x{src:08x},a6
\tjbsr\tosd_{operation}_{size_str}
""".format(**v))
            dest = v["dest"]
            instruction = v["instruction"]
            if "_" in dest:
                dest_address = int(dest.split("_")[-1],16)
                if is_in_ram(dest_address):
                    f.write(f"""\tlea\t0x{dest_address:08x},a6
\tjbsr\tosd_real_ram_address
""")
                else:
                    raise Exception("dest not in RAM: {:08x}".format(dest_address))
                dest = "(a6)"
            f.write(f"\t{instruction}\td7,{dest}\n")
        else:
            # write operation

            src = v["src"]
            instruction = v["instruction"]
            if "_" in src:
                src_address = int(src.split("_")[-1],16)
                if is_in_ram(src_address):
                    f.write(f"""\tlea\t0x{src_address:08x},a6
\tjbsr\tosd_real_ram_address
""")
                src = "(a6)"
            f.write(f"\t{instruction}\t{src},d7\n")

            f.write("""\tlea\t0x{dest:08x},a6
\tjbsr\tosd_{operation}_{size_str}
""".format(**v))

        f.write(f"\tRESTORE_REGS\n\trts\n\n")

