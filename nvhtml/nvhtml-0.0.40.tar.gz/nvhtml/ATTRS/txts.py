from nvhtml.ATTRS.attrsrch import *

def allcls(root,*args,**kwargs):
    clses = srcha4txts(root,"class",*args,**kwargs)
    return(clses)

def cls(root,value,*args,**kwargs):
    txts= srchav4txts("class",value,root,*args,**kwargs)
    if("which" in kwargs):
        which = int(kwargs['which'])
    else:
        which = 0
    if(which == "all"):
        return(txts)
    else:
        return(txts[which])
