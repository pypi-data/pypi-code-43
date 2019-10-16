import ematmap.udlr as udlr
#######################LEVLE 0 可做操作############################
#INIT

def init_mat(layer_length_list,**kwargs):
    '''
        from xdict.jprint import pobj,pdir,parr
        init_mat([1,3,2])
        parr(init_mat([1,3,2]))
        >>> parr(init_mat([1,3,2]))
        [None]
        [None, None, None]
        [None, None]
        >>>
    '''
    value = eftl.dflt_kwargs("value",None,**kwargs)
    dcp = eftl.dflt_kwargs("deepcopy",False,**kwargs)
    value = copy.deepcopy(value) if (dcp) else value
    depth = len(layer_length_list)
    m = elel.init(depth,[])
    for i in range(depth):
        layer_lngth = layer_length_list[i]
        m[i]  = elel.init(layer_lngth,value)
    return(m)

def append_non_empty_lyr(layer,m):
    lngth = len(layer)
    if(lngth == 0):
        pass
    else:
        m.append(layer)
    return(m)


def append_ele_at_depth(depth,ele,m):
    curr_depth = len(m) - 1
    if(depth == curr_depth):
        layer = m[depth]
        layer.append(ele)
    elif(depth == curr_depth + 1):
        m.append([ele])
    else:
        print("Error! can only append-<ele>-to-current-layer or append-a-new-next-layer-[ele]-to-mat")
    return(m)


#SIZE

def get_matsize(m):
    size = 0
    depth = len(m)
    for i in range(depth):
        layer = m[i]
        lngth = len(layer)
        for j in range(lngth):
            size = size + 1
    return(size)


def get_maxlyrlen(m):
    return(elel.max_length(m))


def get_maxlenlyr_depth(m,*args):
    which = eftl.optional_which_arg("all",*args)
    mll = get_maxlyrlen(m)
    depths = elel.cond_select_indexes_all(m,cond_func=lambda ele:len(ele)==mll)
    rslt = depths if(which == "all") else depths[which]
    return(rslt)

def get_maxlenlyr(m,*args):
    which = eftl.optional_which_arg("all",*args)
    depths = get_maxlenlyr_depth(m)
    layers = elel.select_seqs_keep_order(m,depths)
    rslt = layers if(which == "all") else layers[which]
    return(rslt)


# GET 

def xy2loc(x,y):
    return([x,y])

def xy2ele(x,y,m):
    return(m[x][y])

def loc2ele(loc,m):
    x,y = loc
    return(xy2ele(x,y,m))

def ele2loc(ele):
    return((ele.depth,ele.breadth))


# SET

def xyset(x,y,value,m):
    m[x][y] = value
    return(m)

def locset(loc,value,m):
    x,y = loc
    m[x][y] = value
    return(m)


###
# value-of-unique-attribute

def get_uniav2loc_map(m,aname):
    d = {}
    dummy = udlr.mapv(m,lambda ele:d.__setitem__(getattr(ele,aname),ele2loc(ele)))
    return(d)

# value-of-unique-key

def get_unikv2loc_map(m,kname):
    d = {}
    dummy = udlr.mapv(m,lambda ele:d.__setitem__(ele[kname],ele2loc(ele)))
    return(d)

def get_loc2av_map(m,aname):
    d = {}
    dummy = udlr.mapv(m,lambda ele:d.__setitem__(ele2loc(ele),getattr(ele,aname)))
    return(d)


def get_loc2kv_map(m,kname):
    d = {}
    dummy = udlr.mapv(m,lambda ele:d.__setitem__(ele2loc(ele),ele[kname]))
    return(d)



###




#########################################################################


# DEL 
##  DELETE-IS-HIGH-LEVEL-FEATURE-BASE-ON-ID











#################

#ox orig_x
#oy orig_y

#rcrdize         recordize

def rcrdize(m):
    map_func = lambda x,y,v:{"_ox":x,"_oy":y,"_v":v}
    nm = mapxyv(m,map_func=map_func)
    return(nm)

def unrcrdize_x(nm):
    map_func = lambda v:v["_ox"]
    om = mapv(nm,map_func=map_func)
    return(om)

def unrcrdize_y(nm):
    map_func = lambda v:v["_oy"]
    om = mapv(nm,map_func=map_func)
    return(om)

def unrcrdize_v(nm):
    map_func = lambda v:v["_v"]
    om = mapv(nm,map_func=map_func)
    return(om)


def rcrdize_wrapper(f):
    '''
        the data is already wrapped as 
        {
            "_ox":ox,
            "_oy":oy,
            "_v":ov
        }
        so the old map_func  should be wrapped
    '''
    def wrapper(*args,**kwargs):
        mode = dflt_kwargs("mode","v",**kwargs)
        mode = ''.join(list(filter(lambda ele:(ele in "xyv"),mode)))
        which = mode.index("v")
        v = args[which]
        nv = v["_v"]
        ox = v["_ox"]
        oy = v["_oy"]
        args[which] = nv
        nv = f(*args)
        return({
            "_ox":ox,
            "_oy":oy,
            "_v":nv
        })
