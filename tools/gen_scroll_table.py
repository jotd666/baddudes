import bitplanelib
import os,pathlib


this_dir = pathlib.Path(os.path.abspath(__file__)).parent
src_dir = this_dir / os.pardir / "src" / "amiga"

# http://amiga-dev.wikidot.com/hardware:bplcon1

# table with fine shift + byte offset
def doit(asm_output):
    width = 32   # FMODE=1 (64 for FMODE=3)
    wmask = width-1
    scroll_table = [0]*512

    items = []
    for x in range(0,512):
        shift = (wmask-(x & wmask))
        offset = (x // width)*(width//8)
        # pre-encode shift for bplcon

        shiftval_msb = ((shift&(wmask & 0x30))>>2)      # 2 high bits H7 H6
        items.append(shiftval_msb | (shiftval_msb<<4)) # put same shift for both "playfields"
        shiftval_lsb = (shift&0xF)                      # 4 low bits H5->H2
        items.append((shiftval_lsb<<4) | shiftval_lsb) # put same shift for both "playfields"

        items.append(0)
        items.append(offset)

    if asm_output:
        with open(asm_output,"w") as f:
            bitplanelib.dump_asm_bytes(bytes(items),f,True)
    return items

if __name__ == "__main__":
    doit(src_dir / "scroll_table.68k")