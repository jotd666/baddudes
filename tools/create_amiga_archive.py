import subprocess,os,glob,shutil

progdir = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))

gamename = "baddudes"
# JOTD path for cranker, adapt to whatever your path is :)
os.environ["PATH"] += os.pathsep+r"K:\progs\cli"

cmd_prefix = ["make","-f",os.path.join(progdir,"makefile.am")]

subprocess.check_call(cmd_prefix+["clean"],cwd=os.path.join(progdir,"src"))

subprocess.check_call(cmd_prefix+["RELEASE_BUILD=1"],cwd=os.path.join(progdir,"src"))
# create archive

outdir = os.path.join(progdir,f"{gamename}_HD")

if os.path.exists(outdir):
    shutil.rmtree(outdir)

os.mkdir(outdir)

for file in ["readme.md",f"{gamename}.slave"]:  #f"{gamename}.slave",
    shutil.copy(os.path.join(progdir,file),outdir)

datadir = os.path.join(progdir,"data")
shutil.copy(os.path.join(progdir,"assets","amiga","BadDudesAGA.info"),outdir)
dataout = os.path.join(outdir,"data")
shutil.copytree(datadir,dataout)

# cleanup of log files in data dir that whdload creates
for x in glob.glob(os.path.join(dataout,"game_level_?")):
    os.remove(x)
for x in glob.glob(os.path.join(dataout,"level_?_24*")):
    os.remove(x)
for x in glob.glob(os.path.join(dataout,"sprite_ram*")):
    os.remove(x)

#exename = gamename
#subprocess.check_output(["cranker_windows.exe","-f",os.path.join(progdir,exename),"-o",os.path.join(progdir,f"{exename}.rnc")])

subprocess.check_call(cmd_prefix+["clean"],cwd=os.path.join(progdir,"src"))
