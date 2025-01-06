used_name = "game_level_1"

with open(used_name,"rb") as f:
    new_contents = f.read()

with open("sprites/"+used_name,"rb") as f:
    old_contents = f.read()

contents = bytes([a|b for a,b in zip(new_contents,old_contents)])

with open("sprites/"+used_name,"wb") as f:
    f.write(contents)
