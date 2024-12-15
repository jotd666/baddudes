import ira_asm_tools

asmfile = r"K:\jff\AmigaHD\PROJETS\GameRelocs\BadDudes\bad_dudes.s"

af = ira_asm_tools.AsmFile(asmfile)

relocated_ram_offsets = {}

def is_in_ram(ext_address):
    return 0xff8000 <= ext_address <= 0x00ffc000

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
                if prefix=="ext" or prefix=="ram":
                    ext_address = int(rest[0],16)
                    if is_in_ram(ext_address):
                        # in RAM: relocate
                        reloc_address = inst_info["address"]
                        relocated_ram_offsets[(reloc_address,offset)] = arg

with open("patchlist.68k","w") as f:
    f.write("ram_relocs:\n")
    for (reloc,offset),v in sorted(relocated_ram_offsets.items()):
        f.write(f"\t.long\t0x{reloc:06x}+{offset}\t| {v}\n")

