#http://unicode.org/Public/emoji/12.0/

from efdir import fs
import os
import sys
import re
import elist.elist as elel
import edict.edict as eded
from xdict.jprint import pobj,pdir,parr
import dtable.dtable as dtdt
import estring.estring as eses
import string
from nvhtml import htmldb

URLS = {
    'emoji_data':'https://unicode.org/Public/emoji/12.0/emoji-data.txt',
    'emoji_sequence':'https://unicode.org/Public/emoji/12.0/emoji-sequences.txt',
    'emoji_test':'https://unicode.org/Public/emoji/12.0/emoji-test.txt',
    'emoji_variation_sequences':'https://unicode.org/Public/emoji/12.0/emoji-variation-sequences.txt',
    'emoji_zwj_sequences':'https://unicode.org/Public/emoji/12.0/emoji-zwj-sequences.txt'
}

dst_dir = "../estring/emoji/resources/"


srcs = eded.mapkV(URLS,lambda ele:dst_dir+ele+'.orig.txt')


def linize(s):
    s = s.replace("\n\n","\n")
    s = s.replace("\n\n","\n")
    s = s.strip()
    lns = s.split('\n')
    return(lns)

def rm_comments(lns):
    lns = elel.cond_select_values_all(lns, cond_func=lambda ele:not(str.startswith(ele,"#")))
    return(lns)

def emoji_data_line2rvl(line):
    rvl = []
    cache = ""
    first_semi = True
    first_pound = True
    for i in range(len(line)):
        ch = line[i]
        if(ch==';' and first_semi):
            cache = cache.strip()
            rvl.append(cache)
            cache = ''
            first_semi = False
        elif(ch=="#" and first_pound):
            cache = cache.strip()
            rvl.append(cache)
            cache = ''
            first_pound = False
        else:
            cache = cache+ch
    cache = cache.strip()
    cache = eses.replace(cache,re.compile("[ ]{2,}"),"\t")
    cache = cache.strip()
    arr = cache.split("\t")
    pounds = elel.join(arr[:-1]," ")
    pounds = pounds.strip()
    desc = arr[-1]
    desc = desc.strip()
    rvl.append(desc)
    rvl.append(pounds)
    return(rvl)


def emoji_sequence_line2rvl(line):
    rvl = []
    cache = ""
    first_pound = True
    for i in range(len(line)):
        ch = line[i]
        if(ch==';'):
            cache = cache.strip()
            rvl.append(cache)
            cache = ''
        elif(ch=="#" and first_pound):
            cache = cache.strip()
            rvl.append(cache)
            cache = ''
            first_pound = False
        else:
            cache = cache+ch
    cache = cache.strip()
    rvl.append(cache)
    return(rvl)

def emoji_test_line2rvl(line):
    rvl = []
    cache = ""
    first_semi = True
    first_pound = True
    for i in range(len(line)):
        ch = line[i]
        if(ch==';' and first_semi):
            cache = cache.strip()
            rvl.append(cache)
            cache = ''
            first_semi = False
        elif(ch=="#" and first_pound):
            cache = cache.strip()
            rvl.append(cache)
            cache = ''
            first_pound = False
        else:
            cache = cache+ch
    s = cache.strip()
    cache =""
    for i in range(len(s)):
        ch = s[i]
        if(ch in string.ascii_letters):
            pounds = cache.strip()
            desc = s[i:]
            desc = desc.strip()
            break
        else:
            cache = cache + ch
    rvl.append(desc)
    rvl.append(pounds)
    return(rvl)


def emoji_variation_sequences_line2rvl(line):
    rvl = []
    cache = ""
    first_semi = True
    first_pound = True
    for i in range(len(line)):
        ch = line[i]
        if(ch==';' and first_semi):
            cache = cache.strip()
            rvl.append(cache)
            cache = ''
            first_semi = False
        elif(ch=="#" and first_pound):
            cache = cache.strip()
            rvl.append(cache)
            cache = ''
            first_pound = False
        else:
            cache = cache+ch
    s = cache.strip()
    cache =""
    for i in range(len(s)):
        ch = s[i]
        if(ch in string.ascii_uppercase):
            pounds = cache.strip()
            desc = s[i:]
            desc = desc.strip()
            break
        else:
            cache = cache + ch
    rvl.append(desc)
    rvl.append(pounds)
    return(rvl)

emoji_zwj_sequences_line2rvl  = emoji_sequence_line2rvl


def fmt_desc(entry):
    desc = entry[2]
    regex = re.compile("[^0-9a-zA-Z]+")
    desc = eses.replace(desc,regex,"_")
    entry[2] = desc.lower()
    return(entry)


def handle_dotdot(entry):
    ords = entry[0]
    if(".." in entry[0]):
        ords = ords.replace("..","@")
        ords = ords.split("@")
        ords = elel.mapv(ords,int,[16])
        entry[0] = ords
    return(entry)


def split_dotdot_ords(entry):
    ords = entry[0]
    if(isinstance(ords,list)):
        cls = entry[1]
        desc = entry[2]
        pounds = entry[3]
        si = ords[0]
        ei = ords[1] +1
        r =  elel.init_range(si,ei,1)
        entries = elel.mapiv(r,lambda i,ord:[ord,cls,desc+"_"+str(i),pounds])
        return(entries)
    else:
        return([entry])


def reconcat_entries(entries):
    entries = elel.reduce_left(entries,lambda acc,entry:acc+entry,[])
    return(entries)

def handle_multi_ords(entry):
    ords = entry[0]
    if(isinstance(ords,str)):
        ords = eses.split(ords,re.compile("[ ]+")) if(' ' in ords) else [ords]
        ords = elel.mapv(ords,int,[16])
        entry[0] = ords
    else:
        entry[0] = [ords]
    return(entry)


def ords2str(entry):
    ords = entry[0]
    ords = elel.mapv(ords,chr)
    size = len(ords)
    entry.append(size)
    s = elel.join(ords)
    entry[0] = s
    return(entry)

def add_type(entry,name):
    name = name.replace("emoji_","")
    entry.append(name)
    return(entry)

def creat_dtb(name,contents,line2rvls):
    emoji = contents[name]
    emoji_dtb = elel.mapv(emoji,line2rvls[name])
    emoji_dtb = elel.mapv(emoji_dtb,fmt_desc)
    emoji_dtb = elel.mapv(emoji_dtb,handle_dotdot)
    emoji_dtb = elel.mapv(emoji_dtb,split_dotdot_ords)
    emoji_dtb =  reconcat_entries(emoji_dtb)
    emoji_dtb = elel.mapv(emoji_dtb,handle_multi_ords)
    emoji_dtb = elel.mapv(emoji_dtb,ords2str)
    emoji_dtb = elel.mapv(emoji_dtb,add_type,[name])
    return(emoji_dtb)


def contents2mat(contents,kl):
    vl = eded.vlviakl(contents,kl)
    mat = elel.reduce_left(vl,lambda acc,entry:acc+entry,[])
    return(mat)


kl =[
        'emoji_data', 
        'emoji_sequence', 
        'emoji_test', 
        'emoji_variation_sequences', 
        'emoji_zwj_sequences'
]

vl = [
        emoji_data_line2rvl,
        emoji_sequence_line2rvl,
        emoji_test_line2rvl,
        emoji_variation_sequences_line2rvl,
        emoji_zwj_sequences_line2rvl
]

line2rvls = eded.kvlist2d(kl,vl)

contents = eded.mapvV(srcs,lambda ele:fs.rfile(ele))
contents = eded.mapvV(contents,linize)
contents = eded.mapvV(contents,rm_comments)
contents = eded.mapkV(contents,creat_dtb,contents,line2rvls)

fs.wjson(dst_dir+"emoji.cls.json",contents)

#mat
m = contents2mat(contents,kl)
fs.wjson(dst_dir+"emoji.mat.json",m)

#dtb

cnl = ['ord','cls','desc','pounds','size','type']
fs.wjson(dst_dir+"emoji.cnl.json",cnl)

dtb = dtdt.init_dtb(m,cnl)
fs.wjson(dst_dir+"emoji.dtb.json",dtb)

#qtable
qtbl = dtdt.dtb2qtbl(dtb)

#csv
csv = qtbl.df.to_csv()
fs.wfile(dst_dir+"emoji.csv",csv)

#sqlite3
cnx = htmldb.df2sqlite(qtbl,dst_dir+"emoji.sqlite.db","emoji")
cnx.close()


