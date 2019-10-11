#ele                element 
#nd                 wfs-node   same-as ele
#wfsnd              wfs-node   same-as ele

#pele               parent-element  
#
#plmat              mat-of-pathlist


from   eobj import ind
from   eobj import wfsmat_const
from   eobj.primitive import *
import eobj.pathlist_funcs as plfuncs

import efuntool.efuntool as eftl
import elist.elist as elel
import edict.edict as eded
from   ematmap.udlr import mapv
from   ematmap.filter_udlr import vfltre
from   ematmap import utils
import ltdict.ltdict as ltlt



class Wfsmat(list):
    pass


class Ele(ind.Node):
    def __init__(self,*args):
        super().__init__(wfsmat_const.ANL_JOBJ_RONLY,*args)


def is_root(ele):
    return(ele.tag==null)

def init_root():
    root = Ele()
    root.ftag = null      
    #为了统一,所有<实际数据>均从下一层填充 {null:<实际数据>}
    root.fpl = []
    root.pbreadth = null
    root.depth = 0
    root.breadth = 0
    root.sibseq = 0
    root.samefpl_sibseq = 0
    root.samefpl_breadth = 0
    # children will be filled by  plnd-procedure
    root.children = undefined
    # filled later 
    root.dotpath = undefined
    root.mkdir_path = undefined
    return(root)

def init_wfsmat(*args,**kwargs):
    r = eftl.optional_arg(init_root(),*args)
    orig_data = eftl.dflt_kwargs('orig_data',undefined,**kwargs)
    m = Wfsmat([[r]])
    m._orig_data = orig_data
    return(m)

######
def get_loc_via_ele(ele):
    return((ele.depth,ele.breadth))

def get_pele_via_loc(loc,m):
    return(m[loc[0]][loc[1]])

def get_pele_loc_via_ele(ele):
    depth = ele.depth
    pbreadth = ele.pbreadth
    pdepth = depth -1 
    loc = (pdepth,pbreadth)
    return(loc)

def get_pele_via_ele(ele,m):
    loc = get_pele_loc_via_ele(ele)
    return(get_pele_via_loc(loc,m))

######
def set_mat_via_loc(loc,ele,m):
    m[loc[0]][loc[1]] = ele
    return(m)

def set_mat_via_ele(ele,m):
    loc = get_loc_via_ele(ele)
    m[loc[0]][loc[1]] = ele
    return(m)

######
def add_ele_to_mat(ele,mat):
    depth,breadth = get_loc_via_ele(ele)
    mat[depth].append(ele)
    return(mat)


######

#utils
def eleshcmmn(ele):
    ind.shcmmn(ele,wfsmat_const.ANL_JOBJ_RONLY)

def xyshcmmn(x,y,wfsm):
    eleshcmmn(wfsm[x][y])


#######L1
def xy2ele(x,y,wfsm):
    return(wfsm[x][y])

def ele2xy(ele):
    return((ele.depth,ele.breadth))

def ele2loc(ele):
    return((ele.depth,ele.breadth))

def loc2ele(loc,wfsm):
    x,y = loc
    return(xy2ele(x,y,wfsm))


def fpl2ele(fpl,wfsm):
    depth = len(fpl)
    lyr = wfsm[depth]
    fpls = elel.mapv(lyr,lambda ele:ele.fpl)
    index = fpls.index(fpl)
    return(lyr[index])

def fpl2loc(fpl,wfsm):
    ele = fpl2ele(fpl,wfsm)
    return(ele2loc(ele))

def loc2fpl(loc,wfsm):
    ele = loc2ele(loc,wfsm)
    fpl = ele.fpl
    return(fpl)

#####

def is_leaf_ele(ele):
    return(len(ele.children)==0)

def is_leaf_loc(loc):
    ele = loc2ele(loc,wfsm)
    cond = is_leaf_ele(ele)
    return(cond)

def is_leaf_fpl(fpl,m):
    ele = fpl2ele(fpl,wfsm)
    return(is_leaf_ele(ele))




#####
def wfs_eles(wfsm):
    eles = elel.concat(*wfsm)
    return(eles)

def wfs_leaf_eles(wfsm):
    leafs = vfltre(wfsm,cond_func=is_leaf_ele)
    return(leafs)

def wfs_nonleaf_eles(wfsm):
    eles = vfltre(wfsm,cond_func=lambda ele:not(is_leaf_ele(ele)))
    return(eles)

def wfs_leaf_fpls(wfsm):
    leafs = vfltre(wfsm,cond_func=is_leaf_ele)
    fpls = elel.mapv(leafs,lambda ele:ele.fpl)
    return(fpls)

def wfs_nonleaf_fpls(wfsm):
    eles = vfltre(wfsm,cond_func=lambda ele:not(is_leaf_ele(ele)))
    fpls = elel.mapv(eles,lambda ele:ele.fpl)
    return(fpls)

def wfs_leaf_locs(wfsm):
    leafs = vfltre(wfsm,cond_func=is_leaf_ele)
    locs = elel.mapv(leafs,lambda ele:(ele2loc(ele)))
    return(locs)

def wfs_nonleaf_locs(wfsm):
    eles = vfltre(wfsm,cond_func=lambda ele:not(is_leaf_ele(ele)))
    locs = elel.mapv(eles,lambda ele:(ele2loc(ele)))
    return(locs)

###############################

def matsize(m):
    size = 0
    depth = len(m)
    for i in range(depth):
        layer = m[i]
        lngth = len(layer)
        for j in range(lngth):
            size = size + 1
    return(size)


###############################

def is_sibloc(loc0,loc1,m):
    if(loc0 == loc1):
        return(False)
    else:
        pbreadth0 = loc2ele(loc0,m).pbreadth
        pbreadth1 = loc2ele(loc1,m).pbreadth
        cond = (pbreadth0 == pbreadth1)
        return(cond)

def loc2rsibloc(loc,mat):
    depth,breadth = loc
    rsib_breadth = breadth + 1
    layer = mat[depth]
    lngth = len(layer)
    if(rsib_breadth>= lngth):
        return(None)
    else:
        cond = is_sibloc(loc,[depth,rsib_breadth],mat)
        if(cond):
            return((depth,rsib_breadth))
        else:
            return(None)


def loc2ploc(curr_loc,mat):
    depth,breadth = curr_loc
    if(curr_loc ==  (0,0)):
        return(None)
    else:
        pbreadth = mat[depth][breadth].pbreadth
        return((depth-1,pbreadth))


def loc2first_ancestor_rsibloc(curr_loc,mat):
    rsib_loc = loc2rsibloc(curr_loc,mat)
    while(rsib_loc  == None):
        if(curr_loc ==  (0,0)):
            return(None)
        else:
            ploc = loc2ploc(curr_loc,mat)
            rsib_loc = loc2rsibloc(ploc,mat)
            curr_loc = ploc
    return(rsib_loc)

def _edfsl_loc2first_ancestor_rsibloc(curr_loc,edfsl,mat):
    '''
        will append edfsl ,internal using
    '''
    rsib_loc = loc2rsibloc(curr_loc,mat)
    while(rsib_loc  == None):
        if(curr_loc ==  (0,0)):
            return(None)
        else:
            ploc = loc2ploc(curr_loc,mat)
            edfsl.append(ploc)
            rsib_loc = loc2rsibloc(ploc,mat)
            curr_loc = ploc
    return(rsib_loc)


#########################
#wfsel    wfs-ele-list
#sdfsel   sdfs-ele-list
#edfsel   edfs-ele-list

import elist.elist as elel
import edict.edict as eded

def m2wfsel(m):
    l = elel.concat(*m)
    return(l)

def m2wfslocl(m):
    l = m2wfsel(m)
    locl = elel.mapv(l,lambda ele:ele2loc(ele))
    return(locl)

def m2sdfsel(m):
    sdfsel = []
    curr_loc = (0,0)
    count = matsize(m) 
    visited = 0
    while(visited<count):
        sdfsel.append(loc2ele(curr_loc,m))
        x,y = curr_loc
        children = m[x][y].children
        if(children.__len__() == 0):
            curr_loc = loc2first_ancestor_rsibloc(curr_loc,m)
        else:
            curr_loc = children[0]
        visited = visited + 1
    return(sdfsel)

def m2sdfslocl(m):
    sdfslocl = []
    curr_loc = (0,0)
    count = matsize(m)
    visited = 0
    while(visited<count):
        sdfslocl.append(curr_loc)
        x = curr_loc[0]
        y = curr_loc[1]
        children = m[x][y].children
        if(children.__len__() == 0):
            curr_loc = loc2first_ancestor_rsibloc(curr_loc,m)
        else:
            curr_loc = children[0]
        visited = visited + 1
    return(sdfslocl)

def m2edfsel(m):
    edfslocl = m2edfslocl(m)
    edfsl = elel.mapv(edfslocl,loc2ele,[m])
    return(edfsl) 


def m2edfslocl(m):
    edfsl = []
    curr_loc = (0,0)
    count = matsize(m)
    visited = 0
    while(visited<count):
        x = curr_loc[0]
        y = curr_loc[1]
        children = m[x][y].children
        leaf = children.__len__() == 0
        if(leaf):
            # leaf first
            edfsl.append(curr_loc)
            curr_loc = _edfsl_loc2first_ancestor_rsibloc(curr_loc,edfsl,m)
        else:
            curr_loc = children[0]
        visited = visited + 1
    return(edfsl)


#def wfsel2m(wfsel):
#def sdfsel2m(sdfsel):
#def edfsel2m(edfsel):
#因为ele 本身携带位置信息,所以非常容易恢复,使用ltdict

def el2m(el):
    m = {}
    for ele in el:
        depth = ele.depth
        breadth = ele.breadth
        if(depth in m):
            m[depth][breadth] = ele
        else:
            m[depth] = {} 
            m[depth][breadth] = ele
    m = ltlt.ltlt.to_list(m)
    m = elel.mapv(m,lambda lyr:ltlt.ltlt.to_list(lyr))
    return(m)


############################


def wfsel2m(l):
    d = elel.groupby_attr_lngth(l,"fpl")
    kl,vl = eded.d2kvlist(d)
    rslt = elel.sorted_refer_to(vl,kl)
    m = rslt['list']
    return(m)

############################
# 从此处开始改写
############################

def sdfspls2groups(sdfspls,**kwargs):
    '''
        按照深度分层
        一个元素的parent一定在前一层
        sdfsl倒着搜索,一个元素的parent一定是第一个序号小于子pl的元素
        此函数会填充父pl 的index
    '''
    iname = eftl.dflt_kwargs("iname","sdfs_index",**kwargs)
    vname = eftl.dflt_kwargs("vname","fpl",**kwargs)
    descl = elel.l2descl(sdfspls,iname=iname,vname=vname)
    groups = elel.groupby_value_lngth(descl,"fpl")
    kl =list(groups.keys())
    kl.sort()
    kl.reverse()
    for i in range(len(kl)-1):
        k = kl[i]
        layer = groups[k]
        prev_layer = groups[kl[i+1]]
        for each in layer:
            sdfs_index = each['sdfs_index']
            lngth = len(prev_layer)
            si = 0
            for j in range(lngth-1,si-1,-1):
                prev_each = prev_layer[j]
                prev_sdfs_index = prev_each['sdfs_index']
                if(prev_sdfs_index < sdfs_index):
                    each['parent_sdfs_index'] = prev_sdfs_index
                    si = j
                    break
                else:
                    pass
    return(groups)


def sdfspls2wfspls(sdfspls,**kwargs):
    groups = sdfspls2groups(sdfspls,**kwargs)
    vname = eftl.dflt_kwargs("vname","fpl",**kwargs)
    plmat = emem.mapv(groups,map_func=lambda ele:ele[vname])
    plmat = ltlt.to_list(plmat)
    wfsel = m2wfsel(plmat)
    wfspls = elel.mapv(wfsel,lambda ele:ele['fpl'])
    return(wfspls)

#############################################


def edfspls2groups(edfspls):
    '''
        一个元素的parent一定在前一层
        end深度优先搜索,一个元素的parent一定是第一个序号大于子节点的元素
    '''
    iname = eftl.dflt_kwargs("iname","edfs_index",**kwargs)
    vname = eftl.dflt_kwargs("vname","fpl",**kwargs)
    descl = elel.l2descl(edfspls,iname=iname,vname=vname)
    groups = elel.groupby_value_lngth(descl,"fpl")
    kl =list(groups.keys())
    kl.sort()
    kl.reverse()
    for i in range(len(kl)-1):
        k = kl[i]
        layer = groups[k]
        prev_layer = groups[kl[i+1]]
        for each in layer:
            edfs_index = each['edfs_index']
            lngth = len(prev_layer)
            si = 0
            for j in range(si,lngth):
                prev_each = prev_layer[j]
                prev_edfs_index = prev_each['edfs_index']
                if(prev_edfs_index > edfs_index):
                    each['parent_edfs_index'] = prev_edfs_index
                    si = j
                    break
                else:
                    pass
    return(groups)

def edfspls2plmat(edfspls):
    groups = edfspls2groups(edfspls)
    mat =[]
    size = max(list(groups.keys()))
    mat = elel.init(size,[])
    for k in groups:
        depth = k - 1
        layer = groups[k]
        mat[depth].extend(layer)
    return(mat)

def edfspls2plmat(edfspls):
    groups = edfspls2groups(edfspls)
    mat =[]
    size = max(list(groups.keys()))
    mat = elel.init(size,[])
    for k in groups:
        depth = k - 1
        layer = groups[k]
        mat[depth].extend(layer)
    return(mat)


def edfspls2wfspls(edfspls):
    plmat = edfspls2plmat(edfspls)
    plmat = ltlt.to_list(plmat)
    wfsel = m2wfsel(plmat)
    wfspls = elel.mapv(wfsel,lambda ele:ele['fpl'])
    return(wfspls)



def _fdfsl_loc2first_ancestor_rsibloc(curr_loc,fdfsl,mat):
    '''
        will append fdfsl ,internal using
    '''
    rsib_loc = loc2rsibloc(curr_loc,mat)
    while(rsib_loc  == None):
        if(curr_loc ==  (0,0)):
            return(None)
        else:
            ploc = loc2ploc(curr_loc,mat)
            fdfsl.append(ploc)
            rsib_loc = loc2rsibloc(ploc,mat)
            curr_loc = ploc
    return(rsib_loc)

def m2full_dfs_locl(m):
    fdfsl = []
    curr_loc = (0,0)
    count = matsize(m)
    visited = 0
    while(visited<count):
        fdfsl.append(curr_loc)
        x,y = curr_loc
        children = m[x][y].children
        leaf = children.__len__() == 0
        if(leaf):
            # leaf first
            fdfsl.append(curr_loc)
            curr_loc = _fdfsl_loc2first_ancestor_rsibloc(curr_loc,fdfsl,m)
        else:
            curr_loc = children[0]
        visited = visited + 1
    return(fdfsl)


def m2full_fpls(m):
    """
        包括start 与 end 的 全路径
    """
    fdfs_locl = m2full_dfs_locl(m)
    full_fpls = elel.mapv(fdfs_locl,lambda loc:loc2ele(loc,m).fpl)
    return(full_fpls)



#######
#pwfsi                 parent-wfs-index
#plyr               parent-layer

def fpl2pwfsi(fpl,plyr):
    '''
        根据 fpl 找到 parent-wfs-index
    '''
    pfpl = plfuncs.pl2ancespl(fpl,1)
    pb = elel.find_first(plyr,lambda ele:ele.fpl==pfpl)['index']
    pi = plyr[pb].wfs_index
    return(pi)

def pwfsi2pbreadth(pi,plyr):
    '''
       通过wfs_pindex找到 pbreadth
    '''
    pbreadth = elel.find_first(plyr,lambda ele:ele.wfs_index==pi)['index']
    return(pbreadth)


def plmat_fill_pbreadth(plmat):
    plmat[0][0].pbreadth = null
    lngth = len(plmat)
    for i in range(1,lngth):
        lyr = plmat[i]
        plyr = plmat[i-1]
        for j in range(len(lyr)):
            ele = lyr[j]
            pi = ele.wfs_pindex
            plmat[i][j].pbreadth = pwfsi2pbreadth(pi,plyr)
    return(plmat)


def plmat_fill_children(plmat):
    lngth = len(plmat)
    # 先全部填充空children
    for i in range(0,lngth):
        lyr = plmat[i]
        for j in range(len(lyr)):
            ele = lyr[j]
            ele.children = []
    # 然后自底向上填充
    for i in range(lngth-1,0,-1):
        lyr = plmat[i]
        plyr = plmat[i-1]
        for j in range(len(lyr)):
            ele = lyr[j]
            pele = plyr[ele.pbreadth]
            pele.children.append((i,j))
    return(plmat)



def wfsfpls2plmat(wfsfpls,**kwargs):
    iname = eftl.dflt_kwargs("iname","wfs_index",**kwargs)
    vname = eftl.dflt_kwargs("vname","fpl",**kwargs)
    descl = elel.l2descl(wfspls,iname=iname,vname=vname)
    groups = elel.groupby_value_lngth(descl,"fpl")
    plmat = ltlt.to_list(groups) 
    plmat = emem.mapv(plmat,map_func=eded.d2orb)
    plmat[0][0].wfs_pindex = null
    lngth = len(plmat)
    for i in range(1,lngth):
        lyr = plmat[i]
        plyr = plmat[i-1]
        for j in range(len(lyr)):
            ele = lyr[j] 
            pi = fpl2pwfsi(ele.fpl,plyr)
            plmat[i][j].wfs_pindex = pi
    return(plmat)            


###
def plmat2sdfspls(wfsfpls,**kwargs):
    plmat = wfsfpls2plmat(wfsfpls,**kwargs)
    plmat = plmat_fill_pbreadth(plmat)
    plmat = plmat_fill_children(plmat)
    sdfsel = m2sdfsel(plmat)
    sdfspls = elel.mapv(sdfsel,lambda ele:ele.fpl)
    return(sdfspls)


def plmat2edfspls(plmat):
    plmat = wfsfpls2plmat(wfsfpls,**kwargs)
    plmat = plmat_fill_pbreadth(plmat)
    plmat = plmat_fill_children(plmat)
    edfsel = m2edfsel(plmat)
    edfspls = elel.mapv(edfsel,lambda ele:ele.fpl)
    return(edfspls)



###
def wfsfpls2sdfspls(wfsfpls):
    plmat = wfsfpls2plmat(wfsfpls)
    sdfspls = plmat2sdfspls(plmat)
    return(sdfspls)

def wfsfpls2edfspls(wfsfpls):
    plmat = wfsfpls2plmat(wfsfpls)
    edfspls = plmat2edfspls(plmat)
    return(edfspls)




