from   eobj.primitive import *
import eobj.ind as ind 
import eobj.key_fplfuncs as kfplf
import eobj.pathlist_funcs as plfunc
import eobj.wfsmat as wfsmat
from   eobj.kastr import key2attr,attr2key
from   eobj.st import st2ivltd


import edict.edict as eded
import efuntool.etypetool as etytl
import elist.elist as elel
import efuntool.efuntool as eftl
import json

#jobj                  json-like-object ,supoort dict,list,tuple,set,recursive-embeded
#fplnd                 node-with-full-pathlist-and-jobj
#rfplnd                root-fplnd
#root                  root-fplnd
#rnd                   root-fplnd
#r                     root-fplnd

class Node(ind.Node):
    def __init__(self,*args):
        super().__init__(['jobj','ele'],*args)
    def getfpl(self,fpl):
        return(kfplf.getfpl(self.jobj,fpl))

def shcmmn(plnd):
    ind.shcmmn(plnd,['jobj','ele'])


def init_root(jobj):
    root = Node()
    root.jobj = jobj
    ele = wfsmat.init_root()                   #ele.ftag will be null,ele.pbreadth will be null
    ele['type'] = etytl.get_type(jobj)
    ele['ptype'] = null
    ele['im_pjobj'] = null
    ele.children = []                          #init children = [] for next-stage-using
    root.ele = ele
    return(root)

def is_non_leaf(jobj):
    '''
        >>> is_non_leaf({})
        False
        >>> is_non_leaf({1:2})
        True
        >>> is_non_leaf([])
        False
        >>> is_non_leaf([1])
        True
        >>> is_non_leaf(())
        False
        >>> is_non_leaf((1,2))
        True
        >>> is_non_leaf(set({}))
        False
        >>> is_non_leaf(set({3,4,5}))
        True
        >>>
    '''
    cond0 = isinstance(jobj,dict) or isinstance(jobj,list) or isinstance(jobj,tuple) or isinstance(jobj,set)
    return(cond0 and (len(jobj) > 0))

def is_leaf(jobj):
    '''
    '''
    return(not(is_non_leaf(jobj)))

def init_nonleaf_unhandled(root):
    nonleaf_unhandled = [] if(is_leaf(root.jobj)) else [root]
    return(nonleaf_unhandled)



def init_plnd(sibseq,fpl,pele,pjobj):
    '''
        fpl,depth,pbreadth,ftag,sibseq,empty-children
    '''
    plnd = Node()
    plnd.ele = wfsmat.Ele()                                 #init a new-ele, for fill-wfs-mat
    plnd.ele.sibseq = sibseq                                #fill-ele-sibseq
    plnd.ele.fpl = fpl                                      #fill-ele-fpl
    plnd.ele.ftag = plfunc.fpl2ftag(fpl)                    #fill-ele-ftag
    ######
    # pjobj               parent-jobj 
    # specific to handle set
    ptype = etytl.get_type(pjobj)
    if(ptype == "set"):  
        pjobj = list(pjobj)
        plnd.ele['im_pjobj'] = st2ivltd(pjobj)
    else:
        plnd.ele['im_pjobj'] = null
    ######
    jobj = pjobj[plnd.ele.ftag]
    plnd.jobj = jobj                                    #get-current-jobj
    plnd.ele['type'] = etytl.get_type(jobj)             #fill-spec-info-type
    #########################################################################
    plnd.ele['ptype'] = ptype
    #########################################################################
    plnd.ele.pbreadth = pele.breadth                    #fill-ele-pbreadth
    plnd.ele.depth = plfunc.fpl2depth(fpl)              #fill-ele-depth
    plnd.ele.children = []                              #init children = [] for next-stage-using
    return(plnd)


#fpl
#ftagl
#chpls               children-fpls

def get_children(plnd):
    '''
        这一步会填充ele.pbreadth,因为get_children之后,父节点就脱离了,完全依赖pbreadth
        这一步会填充ele.ftag,因为当前层的key(dict) seq(list,tuple)  dummy_seq(set)会在这一层决定
        这一步会填充ele.sibseq, 在兄弟中是第几个
        这一步会填充ele.depth, 在兄弟中是第几个
        这一步会填充ele.fpl, 在兄弟中是第几个
        这一步会填充ele['type'] 这个spec info
    '''
    fpl = plnd.ele.fpl                                    #current fpl  will be used as children pfpl
    jobj = plnd.jobj                                      #current jobj
    if(isinstance(jobj,dict)):
        ftagl,_ = eded.d2kvlist(jobj)                   #get keys-list (ftagl)  
    elif(isinstance(jobj,list) or isinstance(jobj,tuple) or isinstance(jobj,set)):
        ftagl = elel.init_range(0,len(jobj),1)
    else:
        ftagl = []                                            #others all leaf-plnds
    #####
    pfpl = fpl
    chfpls = elel.mapv(ftagl,plfunc.ppl2pl,[pfpl])             #get children-full-pathlist
    #######
    pjobj = jobj
    pele = plnd.ele
    children = elel.mapiv(chfpls,init_plnd,[pele,pjobj])   #get all-children,init_plnd-will-fill-pbreadth=ftag=sibseq,fill-parent-ele-children
    return(children)


def get_layer(nonleaf_unhandled):
    childrens = elel.mapv(nonleaf_unhandled,get_children)
    layer = elel.concat(*childrens)
    return(layer)


def fill_pele_children(ele,wfsm):
    pele = wfsmat.get_pele_via_ele(ele,wfsm)
    pele.children.append(wfsmat.get_loc_via_ele(ele))              #fill-parent-ele-children
    return(pele)

def fill_wfsmat(layer,wfsm):
    '''
        fill  ele.breadth
        这一步会回填parent ele的children
    '''
    lngth = len(layer)
    eftl.ifcall((lngth>0),wfsm.append,[])                                #add-layer-to-wfsmat
    for i in range(lngth):
        plnd = layer[i]
        ele = plnd.ele
        ele.breadth = i                                                  #fill-breadth
        fill_pele_children(ele,wfsm)                                    #fill-parent-ele-children
        wfsm = wfsmat.add_ele_to_mat(ele,wfsm)                           #add-ele-to-wfsmat
    return(layer)


def get_nonleaf_unhandled(layer):
    nonleaf_unhandled = elel.cond_select_values_all(layer,cond_func=lambda plnd:is_non_leaf(plnd.jobj))
    return(nonleaf_unhandled)


def get_jobj_wfsmat(jobj):
    plroot = init_root(jobj)                                           
    #init-plroot     
    wfsm = wfsmat.init_wfsmat(plroot.ele,orig_data=jobj)                           #use-plroot-ele-init-wfsmat     
    nonleaf_unhandled = init_nonleaf_unhandled(plroot)                 
    #fill-nonleaf_unhandled  
    while(len(nonleaf_unhandled)>0):
        layer = get_layer(nonleaf_unhandled)
        layer = fill_wfsmat(layer,wfsm)
        nonleaf_unhandled = get_nonleaf_unhandled(layer)
    return(wfsm)



def shplnd(plnd):
    from xdict.jprint import pobj
    pobj(plnd.jobj)
    wfsmat.shcmmn(plnd.ele)
