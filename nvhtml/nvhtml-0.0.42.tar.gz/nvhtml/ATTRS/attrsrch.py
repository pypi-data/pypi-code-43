from nvhtml import engine
import elist.elist as elel


def srcha4eles(root,attrib,*args,**kwargs):
    xp = "//*[@"+attrib+"]"
    eles = engine.xpath_levels(root,xp,*args,**kwargs)
    return(eles)


def srcha4txts(root,attrib,*args,**kwargs):
    eles = srcha4eles(root,attrib,*args,**kwargs)
    txts = elel.mapv(eles,engine.beautify)
    return(txts)

def srcha4attribs(root,attrib,*args,**kwargs):
    eles = srcha4eles(root,attrib,*args,**kwargs)
    attribs = elel.mapv(eles,lambda ele:ele.attrib[attrib])
    return(attribs)


def srchav4eles(attrib,value,root,*args,**kwargs):
    if("mode" in kwargs):
        mode = kwargs['mode']
    else:
        mode = "multi"
    eles = srcha4eles(root,attrib,*args,**kwargs)
    attribs = srcha4attribs(root,attrib,*args,**kwargs)
    if(mode == "loose"):
        indexes = elel.cond_select_indexes_all(attribs,cond_func=lambda ele:(value in ele))
    elif(mode == "multi"):                    
        indexes = elel.cond_select_indexes_all(attribs,cond_func=lambda ele:(value in ele.split("\x20")))
    else:                                     
        indexes = elel.cond_select_indexes_all(attribs,cond_func=lambda ele:(ele==value))
    eles = elel.select_seqs(eles,indexes)
    return(eles)

def srchav4txts(attrib,value,root,*args,**kwargs):
    eles = srchav4eles(attrib,value,root,*args,**kwargs)
    txts = elel.mapv(eles,engine.beautify)
    return(txts)


def srchav4attribs(attrib,value,root,*args,**kwargs):
    if("mode" in kwargs):
        mode = kwargs['mode']
    else:
        mode = "multi"
    attribs = srcha4attribs(root,attrib,*args,**kwargs)
    if(mode == "loose"):
        attribs = elel.cond_select_values_all(attribs,cond_func=lambda ele:(value in ele))
    elif(mode == "multi"):
        attribs = elel.cond_select_values_all(attribs,cond_func=lambda ele:(value in ele.split("\x20")))
    else:
        attribs = elel.cond_select_values_all(attribs,cond_func=lambda ele:(ele==value))
    return(attribs)



#####


