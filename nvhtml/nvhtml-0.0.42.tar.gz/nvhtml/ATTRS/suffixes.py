from nvhtml import engine
import elist.elist as elel
import edict.edict as eded


def find_all_attribs_include(s,root):
    lngth=s.__len__()
    eles = engine.xpath(root,"//*")
    arr = []
    for ele in eles:
        kl,vl = eded.d2kvlist(ele.attrib)
        arr = elel.concat(arr,vl)
    arr = elel.cond_select_values_all(arr,cond_func = lambda ele:(s == ele[-lngth:]))
    return(arr)


def png(root):
    return(find_all_attribs_include("png",root))

def jpg(root):
    return(find_all_attribs_include("jpg",root))

def svg(root):
    return(find_all_attribs_include("svg",root))

def gif(root):
    return(find_all_attribs_include("gif",root))

def webp(root):
    return(find_all_attribs_include("webp",root))

def mp4(root):
    return(find_all_attribs_include("mp4",root))

def webm(root):
    return(find_all_attribs_include("webm",root))


####




