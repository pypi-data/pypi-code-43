from .k import getsist 
from .v import extprice ,extxmjl,extqyname

def kv(data,krrdict):
    data=getsist(data,krrdict)
    for w in ['zhongbiaoren','zbdl']:
        if w in data.keys():
            data[w]=extqyname(data[w]) 
    for w in ['xmjl']:
        if w in data.keys():
            data[w]=extxmjl(data[w])
    for w in ['zhongbiaojia','kzj']:
        if w in data.keys():
            data[w]=extprice(data[w])
    return data 