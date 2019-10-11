import efuntool.efuntool as eftl
import elist.elist as elel
import copy

#MAP

def _get_fo(x,y,**kwargs):
    map_func = eftl.dflt_kwargs("map_func",lambda ele:ele,**kwargs)
    other_args = eftl.dflt_kwargs("other_args",[],**kwargs)
    map_func_mat = eftl.dflt_kwargs("map_func_mat",None,**kwargs)
    other_args_mat = eftl.dflt_kwargs("other_args_mat",None,**kwargs)
    if(map_func_mat == None):
        pass
    else:
        map_func = map_func_mat[x][y]
    if(other_args_mat == None):
        pass
    else:
        other_args = other_args_mat[x][y]
    return((map_func,other_args))


def udlr_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        lngth = len(m)
        for x in range(lngth):
            layer = m[x]
            llen = len(layer)
            for y in range(llen):
                map_func,other_args = _get_fo(x,y,**kwargs)
                m[x][y] = func({
                    "f":map_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
        return(m)
    return(wrapper)


def udrl_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        lngth = len(m)
        for x in range(lngth):
            layer = m[x]
            llen = len(layer)
            for y in range(llen-1,-1,-1):
                map_func,other_args = _get_fo(x,y,**kwargs)
                m[x][y] = func({
                    "f":map_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
        return(m)
    return(wrapper)



def dulr_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        lngth = len(m)
        for x in range(lngth-1,-1,-1):
            layer = m[x]
            llen = len(layer)
            for y in range(llen):
                map_func,other_args = _get_fo(x,y,**kwargs)
                m[x][y] = func({
                    "f":map_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
        return(m)
    return(wrapper)


def durl_wrap(func):
    @eftl.deepcopy_wrapper
    def wrapper(m,**kwargs):
        lngth = len(m)
        for x in range(lngth-1,-1,-1):
            layer = m[x]
            llen = len(layer)
            for y in range(llen-1,-1,-1):
                map_func,other_args = _get_fo(x,y,**kwargs)
                m[x][y] = func({
                    "f":map_func,
                    "x":x,
                    "y":y,
                    "o":other_args,
                    "m":m
                })
        return(m)
    return(wrapper)


def mapf(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(*other_args)
    return(ele)



def mapx(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,*other_args)
    return(ele)




def mapy(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(y,*other_args)
    return(ele)




def mapv(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(v,*other_args)
    return(ele)




def mapo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(*other_args)
    return(ele)



def mapfx(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,*other_args)
    return(ele)




def mapfy(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(y,*other_args)
    return(ele)



def mapfv(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(v,*other_args)
    return(ele)



def mapfo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(o,*other_args)
    return(ele)


def mapxy(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,y,*other_args)
    return(ele)



def mapxv(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,v,*other_args)
    return(ele)


def mapxo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,*other_args)
    return(ele)


def mapyv(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(y,v,*other_args)
    return(ele)


def mapyo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(y,*other_args)
    return(ele)


def mapvo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(v,*other_args)
    return(ele)


def mapfxy(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,y,*other_args)
    return(ele)


def mapfxv(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,v,*other_args)
    return(ele)


def mapfxo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,o,*other_args)
    return(ele)


def mapfyv(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(y,v,*other_args)
    return(ele)


def mapfyo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(y,o,*other_args)
    return(ele)


def mapfvo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(v,o,*other_args)
    return(ele)


def mapxyv(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,y,v,*other_args)
    return(ele)


def mapxyo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,y,*other_args)
    return(ele)


def mapxvo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,v,*other_args)
    return(ele)



def mapyvo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(y,v,*other_args)
    return(ele)


def mapfxyv(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,y,v,*other_args)
    return(ele)


def mapfxyo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,y,o,*other_args)
    return(ele)


def mapfxvo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,v,o,*other_args)
    return(ele)


def mapfyvo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(y,v,o,*other_args)
    return(ele)


def mapxyvo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,y,v,*other_args)
    return(ele)


def mapfxyvo(d):
    m = d['m']
    map_func = d['f']
    other_args = d['o']
    x = d['x']
    y = d['y']
    v = m[x][y]
    ele = map_func(x,y,v,o,*other_args)
    return(ele)

################

