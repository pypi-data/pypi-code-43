from nvhtml.consts import TAG_DESCS

LVSRCH_ARGUMENTS_TEM = '''def arguments(**kwargs):
    if("source" in kwargs):
        source = kwargs['source']
    else:
        source = True
    if("which" in kwargs):
        which = kwargs['which']
    else:
        which = None
    if("show" in kwargs):
        show = kwargs['show']
    else:
        show = True
    return((source,which,show))\n\n'''

LVSRCH_SRCH_TEM = '''def srch(tag,root,*args,**kwargs):
    source,which,show = arguments(**kwargs)
    args=list(args)
    lngth = args.__len__()
    if(lngth == 0):
        eles = engine.xpath_levels(root,"//"+tag)
    elif(lngth == 1):
        eles = engine.xpath_levels(root,"//"+tag,args[0],args[0]+1)
    else:
        eles = engine.xpath_levels(root,"//"+tag,args[0],args[1])
    if(source):
        eles = elel.mapv(eles,source,[])
    else:
        pass
    if(which==None):
        if(show):
            utils.parr(eles)
        else:
            pass
        return(eles)
    else:
        if(show):
            print(eles[which])
        else:
            pass
        return(eles[which])\n\n'''




LVSRCH_FUNC_TEM = '''def @(root,*args,**kwargs):
    return(srch("@",root,*args,**kwargs))\n\n'''

def gen_lvsrch():
    fd = open("lvsrch.py","w+")
    fd.write("import engine")
    fd.write("\n")
    fd.write("import elist.elist as elel")
    fd.write("\n")
    fd.write("import utils")
    fd.write("\n\n")
    fd.write(LVSRCH_ARGUMENTS_TEM)
    fd.write(LVSRCH_SRCH_TEM)
    for tag in TAG_DESCS:
        content  = LVSRCH_FUNC_TEM.replace("@",tag)
        fd.write(content)
    fd.close()
