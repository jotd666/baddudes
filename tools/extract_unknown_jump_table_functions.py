import os,re

this_dir = os.path.dirname(os.path.abspath(__file__))

jere = re.compile(r"\s+dc\.l\s+lb_(\w+)\b",flags=re.I)
jekre = re.compile(r"\s+dc\.l\s+(\w+)",flags=re.I)

asmfile = r"K:\jff\AmigaHD\PROJETS\GameRelocs\BadDudes\bad_dudes.s"
with open(asmfile) as f:
    lines = list(f)

result = set()

for line in lines:
    if "<data>" in line:
        continue
    m = jere.match(line)
    if m:
        offset = int(m.group(1),0x10)
        if offset < 0x20000:
            result.add(offset)
    else:
        m = jekre.match(line)
        if m:
            print("Known: {}".format(m.group(1)))
with open(r"K:\Emulation\MAME\bkpts","w") as f:
    f.write("bpclear\n")
    for r in sorted(result):
        f.write(f"bpset ${r:04x}\n")

print(len(result))