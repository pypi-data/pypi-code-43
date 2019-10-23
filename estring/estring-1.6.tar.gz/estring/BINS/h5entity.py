from estring.h5entity import h5
from estring.h5entity import _kl
from estring.h5entity import _dkl
from estring.h5entity import _vl
import sys




def tab_strict(dkl,kl,vl,cmd):
    tabs = []
    for i in range(len(kl)):
        dk = dkl[i]
        k = kl[i]
        v = vl[i]
        if(cmd==dk):
            tabs.append((v,'value'))
        elif(dk.startswith(cmd)):
            tabs.append((k,'key'))
        else:
            pass
    return(tabs)


def tab_loose(dkl,kl,vl,cmd):
    tabs = []
    for i in range(len(kl)):
        dk = dkl[i]
        k = kl[i]
        v = vl[i]
        if(cmd==dk):
            tabs.append((v,'value'))
        elif(cmd in dk):
            tabs.append((k,'key'))
        else:
            pass
    return(tabs)


def parr(tabs):
    for t in tabs:
        if(t[1]=='value'):
            print(t[0])
        else:
            print("< "+t[0].strip(';')+" >")


cmd = ""

try:
    cmd = sys.argv[1]
except:
    cmd = ""
else:
    pass

def loose():
    tabs = tab_loose(_dkl,_kl,_vl,cmd)
    parr(tabs)


def strict():
    tabs = tab_strict(_dkl,_kl,_vl,cmd)
    parr(tabs)
