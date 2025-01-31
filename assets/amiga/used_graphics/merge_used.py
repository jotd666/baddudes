import os,pathlib

reference_for_bad_dudes = "game_level_1"

used_name = "game_level_3"

merged_path_file = pathlib.Path("sprites")
# first 512 tiles are the player tiles. Game level 1 has all the moves, so we have to propagate those to
# all other levels. 512*16=8192 first bytes must be copied from level 1 logs

used_dump = os.path.join(r"C:\Users\Public\Documents\Amiga Files\WinUAE",used_name)

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
