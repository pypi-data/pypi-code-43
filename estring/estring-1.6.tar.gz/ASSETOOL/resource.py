from efdir import fs
import os
import sys
import elist.elist as elel
import edict.edict as eded


URLS = {
    'emoji_data':'https://unicode.org/Public/emoji/12.0/emoji-data.txt',
    'emoji_sequence':'https://unicode.org/Public/emoji/12.0/emoji-sequences.txt',
    'emoji_test':'https://unicode.org/Public/emoji/12.0/emoji-test.txt',
    'emoji_variation_sequences':'https://unicode.org/Public/emoji/12.0/emoji-variation-sequences.txt',
    'emoji_zwj_sequences':'https://unicode.org/Public/emoji/12.0/emoji-zwj-sequences.txt'
}

dst_dir = "../estring/emoji/resources/"

def get_cmd(k,v):
    cmd = "wget " + v + " -O " +dst_dir + k
    return(cmd)

d = eded.mapkvV(URLS,get_cmd)

cmds = list(d.values())

elel.for_each(cmds,os.system)



