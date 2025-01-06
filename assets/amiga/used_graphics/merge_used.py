import os
used_name = "game_level_1"

used_dump = os.path.join(r"C:\Users\Public\Documents\Amiga Files\WinUAE",used_name)
with open(used_dump,"rb") as f:
    new_contents = f.read()

with open("sprites/"+used_name,"rb") as f:
    old_contents = f.read()

contents = bytes([a|b for a,b in zip(new_contents,old_contents)])

with open("sprites/"+used_name,"wb") as f:
    f.write(contents)
