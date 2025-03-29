import os,pathlib,shutil,json

from shared import *


used_name = "game_level_3"

merged_path_file = this_dir / "used_graphics" / "sprites"
reference_for_bad_dudes = merged_path_file / "game_level_1"

# first 512 tiles are the player tiles. Game level 1 has all the moves, so we have to propagate those to
# all other levels. 512*16=8192 first bytes must be copied from level 1 logs

data_dir = this_dir / ".." / ".."/"data"

# merge sprites with existing file + moves from level 1
used_dump = data_dir / used_name

with open(merged_path_file / reference_for_bad_dudes,"rb") as f:
    dude_contents_ref = f.read(8192)     # bad dudes marked as used tiles+cluts

if os.path.exists(used_dump):
    with open(used_dump,"rb") as f:
        f.seek(len(dude_contents_ref))
        new_contents = f.read()
else:
    new_contents = bytes(65536 - len(dude_contents_ref))   # new file

# add compete ref for dudes
new_contents = dude_contents_ref + new_contents

if False:  # character moves changed force update
    with open(used_dump,"rb") as f:
        new_contents = f.read()


old_used = merged_path_file / used_name
if old_used.exists():
    with open(old_used,"rb") as f:
        old_contents = f.read()
else:
    old_contents = bytes(65536)

contents = bytes([a|b for a,b in zip(new_contents,old_contents)])

if old_contents == contents:
    print("Nothing new")
else:
    with open(merged_path_file / used_name,"wb") as f:
        f.write(contents)

# move tiles
for file in data_dir.glob("level_?_24?000"):
    print(f"importing {file}")
    dest = merged_path_file / ".." / "tiles" / file.stem

    dest.unlink(missing_ok=True)
    shutil.move(file,dest)
