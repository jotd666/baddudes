import subprocess,os,struct,glob,tempfile
import shutil

this_dir = os.path.dirname(__file__)
gamename = "baddudes"
sox = "sox"

def convert():
    if not shutil.which("sox"):
        raise Exception("sox command not in path, please install it")
    # BTW convert wav to mp3: ffmpeg -i input.wav -codec:a libmp3lame -b:a 330k output.mp3

    #wav_files = glob.glob("sounds/*.wav")


    sound_dir = os.path.join(this_dir,"..","sounds")


    src_dir = os.path.join(this_dir,"../../src/amiga")
    outfile = os.path.join(src_dir,"sounds.68k")
    sndfile = os.path.join(src_dir,"sound_entries.68k")


    hq_sample_rate = 12000  #{"aga":18004,"ecs":12000,"ocs":11025}[mode]
    lq_sample_rate = hq_sample_rate//2 # if aga_mode else 8000


    loop_channel = 3

    EMPTY_SND = "EMPTY_SND"
    sound_dict = {

    "CREDIT_SND"               :{"index":5,"channel":3,"sample_rate":hq_sample_rate,"priority":40},
    "SIREN_SND"               :{"index":0x1D,"channel":3,"sample_rate":hq_sample_rate,"priority":40},
    "TYPEWRITER_SND"               :{"index":0x3D,"channel":3,"sample_rate":hq_sample_rate,"priority":40},
    "PLAYER_HIT_SND"               :{"index":0x2A,"channel":3,"sample_rate":hq_sample_rate,"priority":40},
    "IN_FIRE_SND"               :{"index":0x2D,"channel":3,"sample_rate":hq_sample_rate,"priority":40},
    "FIRE_PUNCH_SND"               :{"index":0x37,"channel":3,"sample_rate":hq_sample_rate,"priority":40},
    "GIRL_SCREAM_SND"               :{"index":0x32,"channel":2,"sample_rate":hq_sample_rate,"priority":40},
    "JUMP_KICK_SND"               :{"index":0x29,"channel":3,"sample_rate":hq_sample_rate,"priority":40},
    #"HELI_KICK_SND"               :{"index":0x1C,"channel":3,"sample_rate":hq_sample_rate,"priority":40},
    "FIRE_SPIT_SND"               :{"index":0xD,"channel":3,"sample_rate":hq_sample_rate,"priority":40},
    #"BOSS_DEAD"               :{"index":0x2F,"channel":2,"sample_rate":hq_sample_rate,"priority":30},
    "BOSS_HIT_SND"               :{"index":0x3A,"channel":2,"sample_rate":hq_sample_rate,"priority":30},
    "BLOW_SND"               :{"index":0x27,"channel":3,"sample_rate":hq_sample_rate,"priority":30},
    #"SABRE_SND"               :{"index":0xB,"channel":3,"sample_rate":hq_sample_rate,"priority":30},
    #"PLAYER_LAND_SND"               :{"index":0x11,"channel":3,"sample_rate":hq_sample_rate,"priority":30},
    "GOT_IT_SND"               :{"index":0x35,"channel":3,"sample_rate":hq_sample_rate,"priority":40},
    "PLAYER_DEAD_SND"               :{"index":0x2B,"channel":3,"sample_rate":hq_sample_rate,"priority":50},
    "DOG_ATTACK_SND"               :{"index":0x33,"channel":3,"sample_rate":hq_sample_rate,"priority":30},
    "DOG_KILLED_SND"               :{"index":0x34,"channel":3,"sample_rate":hq_sample_rate,"priority":30},
    "STAR_THROWN_SND"               :{"index":0x9,"channel":3,"sample_rate":hq_sample_rate,"priority":30},
    "MAN_SCREAM_SND"               :{"index":0x2C,"channel":2,"sample_rate":hq_sample_rate,"priority":30},
    "IM_BAD_SND"               :{"index":0x36,"channel":3,"sample_rate":hq_sample_rate,"priority":30},
    "NINJA_ATTACK_SCREAM_SND"     :{"index":0x3B,"channel":3,"sample_rate":hq_sample_rate,"priority":30},
    "NINJA_CLONE_SND"     :{"index":0x1B,"channel":3,"sample_rate":hq_sample_rate,"priority":40},

    "LEVEL_1_TUNE_SND"                :{"index":0x1F,"pattern":0,"volume":20,'loops':True},
    "LEVEL_2_TUNE_SND"                :{"index":0x20,"pattern":0,"volume":20,'loops':True},
    "KARNOV_TUNE_SND"                :{"index":0x26,"pattern":0,"volume":24,'loops':True},
    "BOSS_TUNE_SND"                :{"index":0x21,"pattern":4,"volume":24,'loops':True},
    "WIN_TUNE_SND"                   :{"index":0x22,"pattern":0,"volume":24,'loops':False,"ticks":180},


    }

    valid_sounds = [None]*128

    for k,v in sound_dict.items():
        valid_sounds[v["index"]] = k
    with open(os.path.join(this_dir,"valid_sound_table.68k"),"w") as f:
        for i,v in enumerate(valid_sounds):
            if v:
                f.write("\t.byte    1\t| {:02x}: {}\n".format(i,v))
            else:
                f.write("\t.byte    0\t| {:02x}\n".format(i))

    max_mod_size = max(os.path.getsize(x) for x in glob.glob(os.path.join(sound_dir,"*.mod")))

    with open(os.path.join(src_dir,"..","sounds.inc"),"w") as f:
        for k,v in sorted(sound_dict.items(),key = lambda x:x[1]["index"]):
            f.write(f"\t.equ\t{k},  0x{v['index']:x}\n")
        f.write(f"\nMAX_MODULE_SIZE = {max_mod_size}\n")

    max_sound = 0x80  # max(x["index"] for x in sound_dict.values())+1
    sound_table = [""]*max_sound
    sound_table_set_1 = ["\t.long\t0,0"]*max_sound




    snd_header = rf"""
    # sound tables
    #
    # the "sound_table" table has 8 bytes per entry
    # first word: 0: no entry, 1: sample, 2: pattern from music module
    # second word: 0 except for music module: pattern number
    # longword: sample data pointer if sample, 0 if no entry and
    # 2 words: 0/1 noloop/loop followed by duration in ticks
    #
    FXFREQBASE = 3579564

        .macro    SOUND_ENTRY    sound_name,size,channel,soundfreq,volume,priority
    \sound_name\()_sound:
        .long    \sound_name\()_raw
        .word   \size
        .word   FXFREQBASE/\soundfreq,\volume
        .byte    \channel
        .byte    \priority
        .endm

    """

    def write_asm(contents,fw):
        n=0
        for c in contents:
            if n%16 == 0:
                fw.write("\n\t.byte\t0x{:x}".format(c))
            else:
                fw.write(",0x{:x}".format(c))
            n += 1
        fw.write("\n")

    music_module_label = f"{gamename}_tunes"

    raw_file = os.path.join(tempfile.gettempdir(),"out.raw")
    with open(sndfile,"w") as fst,open(outfile,"w") as fw:
        fst.write(snd_header)

        fw.write("\t.section\t.datachip\n")
        fw.write("\t.global\t{}\n".format(music_module_label))

        for wav_file,details in sound_dict.items():
            wav_name = os.path.basename(wav_file).lower()[:-4]
            if details.get("channel") is not None:
                fw.write("\t.global\t{}_raw\n".format(wav_name))


        for wav_entry,details in sound_dict.items():
            sound_index = details["index"]

            channel = details.get("channel")
            if channel is None:
                # if music loops, ticks are set to 1 so sound orders only can happen once (else music is started 50 times per second!!)

                sound_table_set_1[sound_index] = "\t.word\t{},{},{}\n\t.byte\t{},{}".format(2,details["pattern"],details.get("ticks",0),details["volume"],int(details["loops"]))
            else:
                wav_name = os.path.basename(wav_entry).lower()[:-4]
                wav_file = os.path.join(sound_dir,wav_name+".wav")

                def get_sox_cmd(sr,output):
                    return [sox,"--volume","0.8",wav_file,"--channels","1","-D","--bits","8","-r",str(sr),"--encoding","signed-integer",output]


                used_sampling_rate = details["sample_rate"]
                used_priority = details.get("priority",1)

                cmd = get_sox_cmd(used_sampling_rate,raw_file)

                subprocess.check_call(cmd)
                with open(raw_file,"rb") as f:
                    contents = f.read()

                # compute max amplitude so we can feed the sound chip with an amped sound sample
                # and reduce the replay volume. this gives better sound quality than replaying at max volume
                # (thanks no9 for the tip!)
                signed_data = [x if x < 128 else x-256 for x in contents]
                maxsigned = max(signed_data)
                minsigned = min(signed_data)

                amp_ratio = max(maxsigned,abs(minsigned))/128

                # JOTD: for that one, I'm using maxxed out sfx by no9, no amp
                amp_ratio = 0.9

                wav = os.path.splitext(wav_name)[0]
                if amp_ratio > 1:
                    print(f"{wav}: volume peaked {amp_ratio}")
                    amp_ratio = 1
                sound_table[sound_index] = "    SOUND_ENTRY {},{},{},{},{},{}\n".format(wav,len(signed_data)//2,channel,used_sampling_rate,int(64*amp_ratio),used_priority)
                sound_table_set_1[sound_index] = f"\t.word\t1,{int(details.get('loops',0))}\n\t.long\t{wav}_sound"

##                if amp_ratio > 0:
##                    maxed_contents = [int(x/amp_ratio) for x in signed_data]
##                else:
##                    maxed_contents = signed_data

                maxed_contents = signed_data

                signed_contents = bytes([x if x >= 0 else 256+x for x in maxed_contents])
                # pre-pad with 0W, used by ptplayer for idling
                if signed_contents[0] != b'\x00' and signed_contents[1] != b'\x00':
                    # add zeroes
                    signed_contents = struct.pack(">H",0) + signed_contents

                contents = signed_contents
                # align on 16-bit
                if len(contents)%2:
                    contents += b'\x00'
                # pre-pad with 0W, used by ptplayer for idling
                if contents[0] != b'\x00' and contents[1] != b'\x00':
                    # add zeroes
                    contents = b'\x00\x00' + contents

                fw.write("{}_raw:   | {} bytes".format(wav,len(contents)))

                if len(contents)>65530:
                    raise Exception(f"Sound {wav_entry} is too long")
                write_asm(contents,fw)


        # make sure next section will be aligned
        fw.write("\t.align\t8\n")


        fst.writelines(sound_table)
        fst.write("\n\t.global\t{0}\n\n{0}:\n".format("sound_table"))
        for i,st in enumerate(sound_table_set_1):
            fst.write(st)
            fst.write(" | {}\n".format(i))


convert()


