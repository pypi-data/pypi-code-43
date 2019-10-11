import efuntool.efuntool as eftl
import elist.elist as elel
import copy

#MAP

def _get_fo(x,y,**kwargs):
    cond_func = eftl.dflt_kwargs("cond_func",lambda ele:ele,**kwargs)
    other_args = eftl.dflt_kwargs("other_args",[],**kwargs)
    cond_func_mat = eftl.dflt_kwargs("cond_func_mat",None,**kwargs)
    other_args_mat = eftl.dflt_kwargs("other_args_mat",None,**kwargs)
    if(cond_func_mat == None):
        pass
    else:
        cond_func = cond_func_mat[x][y]
    if(other_args_mat == None):
        pass
    else:
        other_args = other_args_mat[x][y]
    return((cond_func,other_args))


def udlr_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        rslt = []
        lngth = len(m)
        for x in range(lngth):
            layer = m[x]
            llen = len(layer)
            for y in range(llen):
                cond_func,other_args = _get_fo(x,y,**kwargs)
                cond = func({
                    "f":cond_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
                if(cond):
                    rslt.append(m[x][y])
                else:
                    pass
        return(rslt)
    return(wrapper)


def udrl_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        rslt = []
        lngth = len(m)
        for x in range(lngth):
            layer = m[x]
            llen = len(layer)
            for y in range(llen-1,-1,-1):
                cond_func,other_args = _get_fo(x,y,**kwargs)
                cond = func({
                    "f":cond_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
                if(cond):
                    rslt.append(m[x][y])
                else:
                    pass
        return(rslt)
    return(wrapper)



def dulr_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        rslt = []
        lngth = len(m)
        for x in range(lngth-1,-1,-1):
            layer = m[x]
            llen = len(layer)
            for y in range(llen):
                cond_func,other_args = _get_fo(x,y,**kwargs)
                cond = func({
                    "f":cond_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
                if(cond):
                    rslt.append(m[x][y])
                else:
                    pass
        return(rslt)
    return(wrapper)


def durl_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        rslt = []
        lngth = len(m)
        for x in range(lngth-1,-1,-1):
            layer = m[x]
            llen = len(layer)
            for y in range(llen-1,-1,-1):
                cond_func,other_args = _get_fo(x,y,**kwargs)
                cond = func({
                    "f":cond_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
                if(cond):
                    rslt.append(m[x][y])
                else:
                    pass
        return(rslt)
    return(wrapper)


def ffltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(*other_args)
    return(ele)

def xfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,*other_args)
    return(ele)



def yfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(y,*other_args)
    return(ele)


def vfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(v,*other_args)
    return(ele)


def ofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(*other_args)
    return(ele)



def fxfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,*other_args)
    return(ele)




def fyfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(y,*other_args)
    return(ele)



def fvfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(v,*other_args)
    return(ele)



def fofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(o,*other_args)
    return(ele)


def xyfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,y,*other_args)
    return(ele)



def xvfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,v,*other_args)
    return(ele)


def xofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,*other_args)
    return(ele)


def yvfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(y,v,*other_args)
    return(ele)


def yofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(y,*other_args)
    return(ele)


def vofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(v,*other_args)
    return(ele)


def fxyfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,y,*other_args)
    return(ele)


def fxvfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,v,*other_args)
    return(ele)


def fxofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,o,*other_args)
    return(ele)


def fyvfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(y,v,*other_args)
    return(ele)


def fyofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(y,o,*other_args)
    return(ele)


def fvofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(v,o,*other_args)
    return(ele)


def xyvfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,y,v,*other_args)
    return(ele)


def xyofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,y,*other_args)
    return(ele)


def xvofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,v,*other_args)
    return(ele)



def yvofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(y,v,*other_args)
    return(ele)


def fxyvfltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,y,v,*other_args)
    return(ele)


def fxyofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,y,o,*other_args)
    return(ele)


def fxvofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,v,o,*other_args)
    return(ele)


def fyvofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(y,v,o,*other_args)
    return(ele)


def xyvofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,y,v,*other_args)
    return(ele)


def fxyvofltre(d):
    m = d['m']
    cond_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = cond_func(x,y,v,o,*other_args)
    return(ele)


