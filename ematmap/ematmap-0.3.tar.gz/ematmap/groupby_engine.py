import efuntool.efuntool as eftl
import elist.elist as elel
import copy

#GROUP
#groupd       group-dict
#group        group-key

def _get_fo(x,y,**kwargs):
    group_func = eftl.dflt_kwargs("group_func",lambda ele:ele,**kwargs)
    other_args = eftl.dflt_kwargs("other_args",[],**kwargs)
    group_func_mat = eftl.dflt_kwargs("group_func_mat",None,**kwargs)
    other_args_mat = eftl.dflt_kwargs("other_args_mat",None,**kwargs)
    if(group_func_mat == None):
        pass
    else:
        group_func = group_func_mat[x][y]
    if(other_args_mat == None):
        pass
    else:
        other_args = other_args_mat[x][y]
    return((group_func,other_args))


def _group_add_ele(ele,group,groupd):
    if(group in groupd):
        groupd[group].append(group)
    else:
        groupd[group] = [ele]
    return(groupd)


def udlr_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        groupd = {}
        lngth = len(m)
        for x in range(lngth):
            layer = m[x]
            llen = len(layer)
            for y in range(llen):
                group_func,other_args = _get_fo(x,y,**kwargs)
                group = func({
                    "f":group_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
                groupd = _group_add_ele(m[x][y],group,groupd)
        return(groupd)
    return(wrapper)


def udrl_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        groupd = {}
        lngth = len(m)
        for x in range(lngth):
            layer = m[x]
            llen = len(layer)
            for y in range(llen-1,-1,-1):
                group_func,other_args = _get_fo(x,y,**kwargs)
                group = func({
                    "f":group_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
                groupd = _group_add_ele(m[x][y],group,groupd)
        return(groupd)
    return(wrapper)



def dulr_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        groupd = {}
        lngth = len(m)
        for x in range(lngth-1,-1,-1):
            layer = m[x]
            llen = len(layer)
            for y in range(llen):
                group_func,other_args = _get_fo(x,y,**kwargs)
                group = func({
                    "f":group_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
                groupd = _group_add_ele(m[x][y],group,groupd)
        return(groupd)
    return(wrapper)


def durl_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        groupd = {}
        lngth = len(m)
        for x in range(lngth-1,-1,-1):
            layer = m[x]
            llen = len(layer)
            for y in range(llen-1,-1,-1):
                group_func,other_args = _get_fo(x,y,**kwargs)
                group = func({
                    "f":group_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
                groupd = _group_add_ele(m[x][y],group,groupd)
        return(groupd)
    return(wrapper)


def ffltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(*other_args)
    return(group)

def xfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,*other_args)
    return(group)



def yfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(y,*other_args)
    return(group)


def vfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(v,*other_args)
    return(group)


def ofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(*other_args)
    return(group)



def fxfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,*other_args)
    return(group)




def fyfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(y,*other_args)
    return(group)



def fvfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(v,*other_args)
    return(group)



def fofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(o,*other_args)
    return(group)


def xyfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,y,*other_args)
    return(group)



def xvfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,v,*other_args)
    return(group)


def xofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,*other_args)
    return(group)


def yvfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(y,v,*other_args)
    return(group)


def yofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(y,*other_args)
    return(group)


def vofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(v,*other_args)
    return(group)


def fxyfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,y,*other_args)
    return(group)


def fxvfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,v,*other_args)
    return(group)


def fxofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,o,*other_args)
    return(group)


def fyvfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(y,v,*other_args)
    return(group)


def fyofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(y,o,*other_args)
    return(group)


def fvofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(v,o,*other_args)
    return(group)


def xyvfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,y,v,*other_args)
    return(group)


def xyofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,y,*other_args)
    return(group)


def xvofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,v,*other_args)
    return(group)



def yvofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(y,v,*other_args)
    return(group)


def fxyvfltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,y,v,*other_args)
    return(group)


def fxyofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,y,o,*other_args)
    return(group)


def fxvofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,v,o,*other_args)
    return(group)


def fyvofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(y,v,o,*other_args)
    return(group)


def xyvofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,y,v,*other_args)
    return(group)


def fxyvofltre(d):
    m = d['m']
    group_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    group = group_func(x,y,v,o,*other_args)
    return(group)


