import json


def rbfile(fn):
    fd = open(fn,'rb+')
    rslt = fd.read()
    fd.close()
    return(rslt)

def rfile(fn,codec='utf-8'):
    rslt = rbfile(fn)
    rslt = rslt.decode(codec)
    return(rslt)

def wbfile(fn,content):
    fd = open(fn,'wb+')
    fd.write(content)
    fd.close()

def wfile(fn,content,codec='utf-8'):
    content = content.encode(codec)
    wbfile(fn,content)

def abfile(fn,content):
    fd = open(fn,'ab+')
    fd.write(content)
    fd.close()

def afile(fn,content,codec='utf-8'):
    content = content.encode(codec)
    abfile(fn,content)

def rjson(fn,codec='utf-8'):
    s = rfile(fn,codec)
    d = json.loads(s)
    return(d)

def wjson(fn,js,codec='utf-8'):
    s = json.dumps(js)
    wfile(fn,s,codec)
