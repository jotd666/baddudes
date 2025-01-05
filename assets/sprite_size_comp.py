from PIL import Image,ImageOps
import os,struct,glob,bitplanelib



this_dir = os.path.dirname(os.path.abspath(__file__))

tilesdir = os.path.join(this_dir,"sheets","sprites")

dump_dir = os.path.join(this_dir,"dumps")

datasize = 0

global_palette = set()
for subdir in ["unknown","known"]:
    subdump_dir = os.path.join(dump_dir,subdir)
    for x in glob.glob(os.path.join(subdump_dir,"*.png")):
        img = Image.open(x)
        palette = bitplanelib.palette_extract(img)
        bimg = bitplanelib.palette_image2raw(img,None,palette,generate_mask=1,blit_pad=True)
        datasize += len(bimg)
        global_palette.update(palette)

print("total colors = {}, total size = {}".format(len(global_palette),datasize))
