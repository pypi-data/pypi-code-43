import re
import copy
import elist.elist as elel
import estring.estring as eses
import functools
import tlist.tlist as tltl

#######################



########################

######################################

#kp                   key-path

#kt ktree          key-path-tree              #最外面的[]是容器    old km
#vn vnest          value-in-nested-list       #最外面的[]是容器    old vm

#vndmat        vnest-description-matrix                        

#kpmat          key-path-matrix     (append [] to ktree)
#rvmat          real-value-matrix   (corresponding to kpmat)    

#kdmat          kpmat-description-matrix
#vdmat          rvmat-description-matrix    #refer to kdmat


#是否使用lasy 模式 很纠结，这个Lib纯当一个实验品吧

######################################
# From py3.6, the dict is ordered, try below in 3.6+

def _sort_via_key(d,**kwargs):
    return(_cond_sort(d,**kwargs))

def _sort_via_value(d,**kwargs):
    def eq_func(key1,key2,value1,value2):
        cond = (value1 == value2)
        return(cond)
    def gt_func(key1,key2,value1,value2):
        cond = (value1 > value2)
        return(cond)
    def lt_func(key1,key2,value1,value2):
        cond = (value1 < value2)
        return(cond)
    return(_cond_sort(d,lt_func=lt_func,eq_func=eq_func,gt_func=gt_func,**kwargs))



def _cond_sort(d,**kwargs):
    '''
    '''
    def default_eq_func(key1,key2,value1,value2):
        cond = (key1 == key2)
        return(cond)
    def default_gt_func(key1,key2,value1,value2):
        cond = (key1 > key2)
        return(cond)
    def default_lt_func(key1,key2,value1,value2):
        cond = (key1 < key2)
        return(cond)
    if('eq_func' in kwargs):
        eq_func = kwargs['eq_func']
    else:
        eq_func = default_eq_func
    if('gt_func' in kwargs):
        gt_func = kwargs['gt_func']
    else:
        gt_func = default_gt_func
    if('lt_func' in kwargs):
        lt_func = kwargs['lt_func']
    else:
        lt_func = default_lt_func
    if('eq_func_args' in kwargs):
        eq_func_args = kwargs['eq_func_args']
    else:
        eq_func_args = []
    if('gt_func_args' in kwargs):
        gt_func_args = kwargs['gt_func_args']
    else:
        gt_func_args = []
    if('lt_func_args' in kwargs):
        lt_func_args = kwargs['lt_func_args']
    else:
        lt_func_args = []
    if('reverse' in kwargs):
        reverse = kwargs['reverse']
    else:
        reverse = False
    tl = dict2tlist(d)
    def cmp_func(ele1,ele2):
        '''
        '''
        cond1 = lt_func(ele1[0],ele2[0],ele1[1],ele2[1])
        cond2 = eq_func(ele1[0],ele2[0],ele1[1],ele2[1])
        cond3 = gt_func(ele1[0],ele2[0],ele1[1],ele2[1])
        if(cond1):
            return(-1)
        elif(cond2):
            return(0)
        else:
            return(1)
    ntl = sorted(tl,key=functools.cmp_to_key(cmp_func),reverse=reverse)
    nd = tlist2dict(ntl)
    return(nd)

def _reorder_via_klist(d,nkl,**kwargs):
    '''
        d = {'scheme': 'http', 'path': '/index.php', 'params': 'params', 'query': 'username=query', 'fragment': 'frag', 'username': '', 'password': '', 'hostname': 'www.baidu.com', 'port': ''}
        pobj(d)
        nkl = ['scheme', 'username', 'password', 'hostname', 'port', 'path', 'params', 'query', 'fragment']
        pobj(_reorder_via_klist(d,nkl))
    '''
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = True
    if(deepcopy):
        d = copy.deepcopy(d)
    else:
        pass
    nd = {}
    lngth = nkl.__len__()
    for i in range(0,lngth):
        k = nkl[i]
        nd[k] = d[k]
    return(nd)



def _reorder_via_vlist(d,nvl,**kwargs):
    '''
    '''
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = True
    if(deepcopy):
        d = copy.deepcopy(d)
    else:
        pass
    nd = {}
    lngth = nvl.__len__()
    for i in range(0,lngth):
        v = nvl[i]
        ks = _keys_via_value_nonrecur(d,v)
        for j in range(0,ks.__len__()):
            k = ks[j]
            nd[k] = d[k]
    return(nd)


# From py3.6, the dict is ordered, try upper in 3.6+
#######################################

def _getitem2(k,d):
    return(d[k])

def _getitem(d,k):
    return(d[k])

#######################################
def _select_norecur_via_value(d,*vs,**kwargs):
    vs = list(vs)
    lngth = vs.__len__()
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = True
    if(deepcopy):
        nd = copy.deepcopy(d)
    else:
        nd = d
    rslt = {}
    for i in range(0,lngth):
        v = vs[i]
        ks = _keys_via_value_nonrecur(d,v)
        for j in range(0,ks.__len__()):
            k = ks[j]
            rslt[k] = d[k]
    return(rslt)


def _select_norecur(d,*ks,**kwargs):
    ks = list(ks)
    lngth = ks.__len__()
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = True
    if(deepcopy):
        nd = copy.deepcopy(d)
    else:
        nd = d
    rslt = {}
    for i in range(0,lngth):
        k = ks[i]
        if(k in nd):
            rslt[k] = nd[k]
        else:
            pass
    return(rslt)



def _get_depth(d):
    kt,vn = _d2kvmatrix(d)
    dpth = kt.__len__()
    return(dpth)


def _get_sib_paths(d,keypath,**kwargs):
    '''
        
    '''
    lngth = keypath.__len__()
    kwargs['from_lv'] = lngth
    kwargs['to_lv'] = lngth 
    return(_tree_paths(d,**kwargs))


def _tree_paths(d,**kwargs):
    dpth = _get_depth(d)
    if('leaf_only' in kwargs):
        leaf_only = kwargs['leaf_only']
    else:
        leaf_only = False
    if('non_leaf_only' in kwargs):
        non_leaf_only = kwargs['non_leaf_only']
    else:
        non_leaf_only = False
    if('from_lv' in kwargs):
        from_lv = kwargs['from_lv']
    else:
        from_lv = 1
    if('to_lv' in kwargs):
        to_lv = kwargs['to_lv']
    else:
        to_lv = dpth
    if('show' in kwargs):
        show = kwargs['show']
    else:
        show = True
    kdfs = _get_kdfs(d)
    tr = elel.filter(kdfs,kmdfs_cond_func,d,from_lv,to_lv,leaf_only,non_leaf_only)
    if(show):
        elel.forEach(tr,print)
    else:
        pass
    return(tr)




#######################################
def _ancestor_keypaths(keypath):
    '''
        keypath = ['y', 'xx', 'x2']
        
    '''
    akps = elel.ListTree.ancestlize(keypath)
    return(akps)


def _ancestors(d,keypath):
    '''
    '''
    akps = elel.ListTree.ancestlize(keypath)
    ancs = elel.array_map(akps,_getitem_via_pathlist2,d)
    return(ancs)



def _parent_keypath(keypath):
    '''
        keypath = ['y', 'xx', 'x2']

    '''
    pkp = keypath[:-1]
    return(pkp)



def _parent(d,keypath):
    '''
    '''
    pkp = keypath[:-1]
    p = _getitem_via_pathlist(d,pkp)
    return(p)


def _descendant_keypaths(d,keypath,**kwargs):
    kt,vn = _d2kvmatrix(d)
    kdmat = _scankm(kt)
    loc = get_kdmat_loc(kdmat,keypath)
    ldps = kdmat[loc[0]][loc[1]]['leaf_descendant_paths']
    nldps = kdmat[loc[0]][loc[1]]['non_leaf_descendant_paths']
    if('leaf_only' in kwargs):
        return(copy.deepcopy(ldps))
    elif('non_leaf_only' in kwargs):
        return(copy.deepcopy(nldps))
    else:
        dkps = copy.deepcopy(ldps)
        dkps.extend(nldps)
        return(dkps)

def _descendants(d,keypath,**kwargs):
    dkps = _descendant_keypaths(d,keypath,**kwargs)
    arr = elel.array_map(dkps,_getitem_via_pathlist2,d)
    return(arr)


#######################################
def cmdpl_in_cmdpl(cmdpl1,cmdpl2,**kwargs):
    cmd_pl1 = copy.deepcopy(cmdpl1)
    cmd_pl2 = copy.deepcopy(cmdpl2)
    cmdpl1 = []
    for i in range(0,cmd_pl1.__len__()):
        v = cmd_pl1[i]
        v = str(v)
        cmdpl1.append(v)
    cmdpl2 = []
    for i in range(0,cmd_pl2.__len__()):
        v = cmd_pl2[i]
        v = str(v)
        cmdpl2.append(v)
    if('mode' in kwargs):
        mode = kwargs['mode']
    else:
        mode = 'strict'
    cmdpl1_len = cmdpl1.__len__()
    cmdpl2_len = cmdpl2.__len__()
    if(cmdpl1_len > cmdpl2_len):
        return(False)
    else:
        pass
    if(mode == 'strict'):
        if(cmdpl1_len == 0):
            return(True)
        elif(cmdpl1_len==1):
            start1 = cmdpl1[0]
            start2 = cmdpl2[0]
            cond = eses.startsWith(start2,start1)
            if(cond):
                return(True)
            else:
                return(False)
        else:
            for i in range(0,cmdpl1_len-1):
                if(cmdpl1[i]==cmdpl2[i]):
                    pass
                else:
                    return(False)
            end1 = cmdpl1[cmdpl1_len-1]
            end2 = cmdpl2[cmdpl1_len-1]
            cond = eses.startsWith(end1,end2)
            if(cond):
                return(True)
            else:
                return(False)
    else:
        if(cmdpl1_len == 0):
            return(True)
        elif(cmdpl1_len==1):
            ele1 = cmdpl1[0]
            for i in range(0,cmdpl2_len):
                ele2 = cmdpl2[i]
                cond = (ele1 in ele2)
                if(cond):
                    return(True)
                else:
                    pass
            return(False)
        else:
            #---------debug--------#
            def try_to_find_match(lb2,cmdpl1_len,cmdpl2_len,cmdpl1,cmdpl2):
                distance = lb2 - 1
                if(lb2>cmdpl2_len - 1):
                    return((False,0,distance))
                else:
                    i = -1
                    for i in range(1,cmdpl1_len-1):
                        index = i + distance
                        if(index > (cmdpl2_len -1)):
                            return((False,i,distance))
                        else:
                            if(cmdpl1[i]==cmdpl2[index]):
                                pass
                            else:
                                return((False,i,distance))
                    return((True,i,distance))
            #---------debug--------#
            lb2 = 0
            finded = 0
            start1 = cmdpl1[0]
            for j in range(0,cmdpl2_len):
                start2 = cmdpl2[j]
                cond = eses.endsWith(start2,start1)
                if(cond):
                    lb2 = j+1
                    finded,lb1,distance = try_to_find_match(lb2,cmdpl1_len,cmdpl2_len,cmdpl1,cmdpl2)
                    if(finded):
                        break
                    else:
                        pass
                else:
                    pass
            if(finded):
                pass
            else:
                return(False)
            if(lb2>cmdpl2_len - 1):
                return(False)
            else:
                index = cmdpl1_len-1+distance
                if(index > (cmdpl2_len -1)):
                    return(False)
                else:
                    end1 = cmdpl1[cmdpl1_len-1]
                    end2 = cmdpl2[index]
                    cond = eses.startsWith(end2,end1)
                    if(cond):
                        return(True)
                    else:
                        return(False)

######################################


def _cond_select_keypath(d,keypath,*args,**kwargs):
    '''
    '''
    if('mode' in kwargs):
        mode = kwargs['mode']
    else:
        mode = 'loose'
    def cond_func(ele,keypath):
        cond = cmdpl_in_cmdpl(keypath,ele,mode=mode)
        return(cond)
    kdfs = _get_kdfs(d)
    rslt = elel.filter(kdfs,cond_func,keypath)
    return(rslt)



#######################################
def _get_kdfs(d):
    tr,nest = _d2kvmatrix(d)
    vwfs1 = elel.get_wfs(nest)
    rslt = get_kmdfs(tr,vwfs1)
    return(rslt)


kpldfs = _get_kdfs




def _get_vndmat(d):
    kt,vn = _d2kvmatrix(d)
    vndmat = elel.ListTree(vn).desc
    return(vndmat)

def _get_kpmat(d):
    kt,vn = _d2kvmatrix(d)
    kpmat = elel.prepend(kt,[])
    return(kpmat)


def _get_kdmat(d):
    kt,vn = _d2kvmatrix(d)
    kdmat = _scankm(kt)
    return(kdmat)
    


#######################################
#non-recursive
def _keys_via_value_nonrecur(d,v):
    '''
        #non-recursive
        d = {1:'a',2:'b',3:'a'}
        _keys_via_value_nonrecur(d,'a')
    '''
    rslt = []
    for key in d:
        if(d[key] == v):
            rslt.append(key)
    return(rslt)


######################################
#recursive
def _keys_via_value(d,value,**kwargs):
    '''
        d = {
         'x':
              {
               'x2': 'x22',
               'x1': 'x11'
              },
         'y':
              {
               'y1': 'v1',
               'y2':
                     {
                      'y4': 'v4',
                      'y3': 'v3',
                     },
               'xx': 
                    {
                        'x2': 'x22',
                        'x1': 'x11'
                  }
              },
         't': 20,
         'u':
              {
               'u1': 20
              }
        }
    '''
    km,vm = _d2kvmatrix(d)
    rvmat = _get_rvmat(d)
    depth = rvmat.__len__()
    ##
    #print(km)
    ##
    kdmat = _scankm(km)
    if('leaf_only' in kwargs):
        leaf_only = kwargs['leaf_only']
    else:
        leaf_only = False
    if('non_leaf_only' in kwargs):
        non_leaf_only = kwargs['non_leaf_only']
    else:
        non_leaf_only = False
    if('from_lv' in kwargs):
        from_lv = kwargs['from_lv']
    else:
        from_lv = 1
    if('to_lv' in kwargs):
        to_lv = kwargs['to_lv']
    else:
        if('from_lv' in kwargs):
            to_lv = from_lv
        else:
            to_lv = depth
    rslt = []
    for i in range(from_lv,to_lv):
        rvlevel = rvmat[i]
        for j in range(0,rvlevel.__len__()):
            v = rvlevel[j]
            cond1 = (v == value)
            if(leaf_only == True):
                cond2 = (kdmat[i][j]['leaf'] == True)
            elif(non_leaf_only == True):
                cond2 = (kdmat[i][j]['leaf'] == False)
            else:
                cond2 = True
            cond = (cond1 & cond2)
            if(cond):
                rslt.append(kdmat[i][j]['path'])
            else:
                pass
    return(rslt)

pathlists_via_value = _keys_via_value


def _bracket_lists_via_value(d,value,**kwargs):
    '''
    '''
    kpls = _keys_via_value(d,value,**kwargs)
    brls = elel.array_map(kpls,elel.pathlist_to_getStr)
    return(brls)


def kpls2brls(kpls):
    brls = elel.array_map(kpls,elel.pathlist_to_getStr)
    return(brls)

def brls2kpls(brls):
    kpls = elel.array_map(brls,elel.getStr_to_pathlist)
    return(kpls)


######################################

def _contains(d,value,**kwargs):
    kpls = _keys_via_value(d,value,**kwargs)
    if(kpls.__len__() == 0):
        return(False)
    else:
        return(True)

######################################

def _count(d,value,**kwargs):
    kpls = _keys_via_value(d,value,**kwargs)
    return(kpls.__len__())

######################################

def d2kvlist(d):
    '''
        d = {'GPSImgDirectionRef': 'M', 'GPSVersionID': b'\x02\x03\x00\x00', 'GPSImgDirection': (21900, 100)}
        pobj(d)
        kl,vl = d2kvlist(d)
        pobj(kl)
        pobj(vl)
    '''
    kl = list(d.keys())
    vl = list(d.values())
    return((kl,vl))

def kvlist2d(kl,vl):
    '''
    '''
    d = {}
    for i in range(0,kl.__len__()):
        k = kl[i]
        v = vl[i]
        d[k] = v
    return(d)

def vlviakl(d,kl):
    vl = []
    for i in range(kl.__len__()):
        k = kl[i]
        vl.append(d[k])
    return(vl)


def klviavl(d,vl):
    '''
        must be 1:1 map
    '''
    dkl,dvl = d2kvlist(d)
    kl = []
    for i in range(vl.__len__()):
        v = vl[i]
        index = dvl.index(v)
        kl.append(dkl[index])
    return(kl)

    


####
def list2d(arr):
    kl = elel.select_evens(arr)
    vl = elel.select_odds(arr)
    d = kvlist2d(kl,vl)
    return(d)

def d2list(d):
    kl = list(d.keys())
    vl = list(d.values())
    l = elel.interleave(kl,vl)
    return(l)

#
def brkl2d(arr,interval):
    '''
        arr = ["color1","r1","g1","b1","a1","color2","r2","g2","b2","a2"]
        >>> brkl2d(arr,5)
        [{'color1': ['r1', 'g1', 'b1', 'a1']}, {'color2': ['r2', 'g2', 'b2', 'a2']}]
    '''
    lngth = arr.__len__()
    brkseqs = elel.init_range(0,lngth,interval)
    l = elel.broken_seqs(arr,brkseqs)
    d = elel.mapv(l,lambda ele:{ele[0]:ele[1:]})
    return(d)

#def d2brkl(d)    

####
#dele dict-element

def dele2t(d):
    '''
    '''
    k = list(d.keys())[0]
    v = list(d.values())[0]
    return((k,v))

def t2dele(t):
    '''
    '''
    return({t[0]:t[1]})

#_vksdesc value-keys-description
def _vksdesc(d):
    '''
        d = {'a':1,'b':2,'c':2,'d':4}
        desc = _vksdesc(d)
        pobj(desc)
    '''
    pt = copy.deepcopy(d)
    seqs_for_del =[]
    vset = set({})
    for k in pt:
        vset.add(pt[k])
    desc = {}
    for v in vset:
        desc[v] = []
    for k in pt:
        desc[pt[k]].append(k)
    return(desc)

#
def tlist2dict(tuple_list,**kwargs):
    '''
        #duplicate keys will lost
        tl = [(1,2),(3,4),(1,5)]
        tlist2dict(tl)
    '''
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 1
    if(check):
        if(tltl.is_tlist(tuple_list)):
            pass
        else:
            return(None)
    else:
        pass
    j = {}
    if(deepcopy):
        new = copy.deepcopy(tuple_list)
    else:
        new = tuple_list
    for i in range(0,new.__len__()):
        temp = new[i]
        key = temp[0]
        value = temp[1]
        j[key] = value
    return(j)

def dict2tlist(this_dict,**kwargs):
    '''
        #sequence will be losted
        d = {'a':'b','c':'d'}
        dict2tlist(d)
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 1
    if(check):
        if(isinstance(this_dict,dict)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    tuple_list = []
    if(deepcopy):
        new = copy.deepcopy(this_dict)
    else:
        new = this_dict
    i = 0
    for key in this_dict:
        value = this_dict[key]
        tuple_list.append((key,value))
    return(tuple_list)

###

def is_mirrable(d):
    '''
        d = {1:'a',2:'a',3:'b'}
    '''
    vl = list(d.values())
    lngth1 = vl.__len__()
    uvl = elel.uniqualize(vl)
    lngth2 = uvl.__len__()
    cond = (lngth1 == lngth2)
    return(cond)

def dict_mirror(d,**kwargs):
    '''
        d = {1:'a',2:'a',3:'b'}
    '''
    md = {}
    if('sort_func' in kwargs):
        sort_func = kwargs['sort_func']
    else:
        sort_func = sorted
    vl = list(d.values())
    uvl = elel.uniqualize(vl)
    for v in uvl:
        kl = _keys_via_value_nonrecur(d,v)
        k = sorted(kl)[0]
        md[v] = k
    return(md)

def _text_cond(text,condmatch,*args):
    if(type(condmatch)==type("")):
        if(condmatch in text):
            return(True)
        else:
            return(False)
    elif(type(condmatch) == type(re.compile(""))):
        m = condmatch.search(text)
        if(m):
            return(True)
        else:
            return(False)
    else:
        return(condmatch(text,*args))

def _cond_select_key_nonrecur(d,cond_match=None,**kwargs):
    '''
        d = {
            "ActiveArea":"50829", 
            "Artist":"315",                 
            "AsShotPreProfileMatrix":"50832",
            "AnalogBalance":"50727",          
            "AsShotICCProfile":"50831",       
            "AsShotProfileName":"50934",
            "AntiAliasStrength":"50738",      
            "AsShotNeutral":"50728",          
            "AsShotWhiteXY":"50729"
        }
        _cond_select_key_nonrecur(d,"An")
        _cond_select_key_nonrecur(d,"As")
        regex = re.compile("e$")
        _cond_select_key_nonrecur(d,regex)
    '''
    if('cond_func' in kwargs):
        cond_func = kwargs['cond_func']
    else:
        cond_func = _text_cond
    if('cond_func_args' in kwargs):
        cond_func_args = kwargs['cond_func_args']
    else:
        cond_func_args = []
    rslt = {}
    for key in d:
        if(cond_func(key,cond_match,*cond_func_args)):
            rslt[key] = d[key]
        else:
            pass
    return(rslt)

def _cond_select_value_nonrecur(d,cond_match=None,**kwargs):
    '''
        d = {
            "ActiveArea":"50829", 
            "Artist":"315",                 
            "AsShotPreProfileMatrix":"50832",
            "AnalogBalance":"50727",          
            "AsShotICCProfile":"50831",       
            "AsShotProfileName":"50934",
            "AntiAliasStrength":"50738",      
            "AsShotNeutral":"50728",          
            "AsShotWhiteXY":"50729"
        }
        _cond_select_value_nonrecur(d,"50")
        _cond_select_value_nonrecur(d,"72")
        regex = re.compile("8$")
        _cond_select_value_nonrecur(d,regex)
    '''
    if('cond_func' in kwargs):
        cond_func = kwargs['cond_func']
    else:
        cond_func = _text_cond
    if('cond_func_args' in kwargs):
        cond_func_args = kwargs['cond_func_args']
    else:
        cond_func_args = []
    rslt = {}
    for key in d:
        value = d[key]
        if(cond_func(value,cond_match,*cond_func_args)):
            rslt[key] = d[key]
        else:
            pass
    return(rslt)


def _cond_select_leaf_value(d,cond_ele,*args,**kwargs):
    '''
    '''
    if('mode' in kwargs):
        mode = kwargs['mode']
    else:
        mode = 'loose'
    tr,vnest = _d2kvmatrix(d)
    vltr = elel.ListTree(vnest)
    flat = vltr.flatten()
    t = type(cond_ele)
    if(t == type('')):
        if(mode == 'loose'):
            rslt = elel.select_loose_in(flat,cond_ele)
        else:
            rslt = elel.select_strict_in(flat,cond_ele)
    elif(t == type(re.compile(''))):
        rslt = elel.select_regex_in(flat,cond_ele)
    elif(t == type(lambda x:x)):
        cond_func = cond_ele
        if('cond_func_args' in kwargs):
            cond_func_args = kwargs['cond_func_args']
        else:
            cond_func_args = []
        rslt = elel.cond_select_values_all2(flat,cond_func=cond_func, cond_func_args = cond_func_args)
    else:
        rslt = flat
    return(rslt)


def _diff_internal(d1,d2):
    '''
        d1 = {'a':'x','b':'y','c':'z'}
        d2 = {'a':'x','b':'u','d':'v'}
        _diff_internal(d1,d2)
        _diff_internald2,d1)
    '''
    same =[]
    kdiff =[]
    vdiff = []
    for key in d1:
        value = d1[key]
        if(key in d2):
            if(value == d2[key]):
                same.append(key)
            else:
                vdiff.append(key)
        else:
            kdiff.append(key)
    return({'same':same,'kdiff':kdiff,'vdiff':vdiff})

#并集
def _union(d1,d2):
    '''
        d1 = {'a':'x','b':'y','c':'z'}
        d2 = {'a':'x','b':'u','d':'v'}
        _union(d1,d2)
        _union(d2,d1)
    '''
    u = {}
    ds = _diff_internal(d1,d2)
    for key in ds['same']:
        u[key] = d1[key]
    for key in ds['vdiff']:
        u[key] = d1[key]
    for key in ds['kdiff']:
        u[key] = d1[key]
    ds = _diff_internal(d2,d1)
    for key in ds['kdiff']:
        u[key] = d2[key]
    return(u)


#差集
def _diff(d1,d2):
    '''
        d1 = {'a':'x','b':'y','c':'z'}
        d2 = {'a':'x','b':'u','d':'v'}
        _diff(d1,d2)
        _diff(d2,d1)
    '''
    d = {}
    ds = _diff_internal(d1,d2)
    for key in ds['vdiff']:
        d[key] = d1[key]
    for key in ds['kdiff']:
        d[key] = d1[key]
    return(d)

#交集

def _intersection(d1,d2):
    '''
        d1 = {'a':'x','b':'y','c':'z'}
        d2 = {'a':'x','b':'u','d':'v'}
        _intersection(d1,d2)
        _intersection(d2,d1)
    '''
    i = {}
    ds = _diff_internal(d1,d2)
    for key in ds['same']:
        i[key] = d1[key]
    return(i)

#补集
def _complement(d1,d2):
    '''
        d1 = {'a':'x','b':'y','c':'z'}
        d2 = {'a':'x','b':'u','d':'v'}
        complement(d1,d2)
        complement(d2,d1)
    '''
    u = _union(d1,d2)
    c = _diff(u,d1)
    return(c)

def _uniqualize(d):
    '''
        d = {1:'a',2:'b',3:'c',4:'b'}
        _uniqualize(d)
    '''
    pt = copy.deepcopy(d)
    seqs_for_del =[]
    vset = set({})
    for k in pt:
        vset.add(pt[k])
    tslen = vset.__len__()
    freq = {}
    for k in pt:
        v = pt[k]
        if(v in freq):
            freq[v] = freq[v] + 1
            seqs_for_del.append(k)
        else:
            freq[v] = 0
    npt = {}
    for k in pt:
        if(k in seqs_for_del):
            pass
        else:
            npt[k] = pt[k]
    pt = npt
    return(npt)

def _extend(dict1,dict2,**kwargs):
    '''
        dict1 = {1:'a',2:'b',3:'c',4:'d'}
        dict2 = {5:'u',2:'v',3:'w',6:'x',7:'y'}
        d = _extend(dict1,dict2)
        pobj(d)
        dict1 = {1:'a',2:'b',3:'c',4:'d'}
        dict2 = {5:'u',2:'v',3:'w',6:'x',7:'y'}
        d = _extend(dict1,dict2,overwrite=1)
        pobj(d)
    '''
    if('deepcopy' in kwargs):
        deepcopy=kwargs['deepcopy']
    else:
        deepcopy=1
    if('overwrite' in kwargs):
        overwrite=kwargs['overwrite']
    else:
        overwrite=0
    if(deepcopy):
        dict1 = copy.deepcopy(dict1)
        dict2 = copy.deepcopy(dict2)
    else:
        pass
    d = dict1
    for key in dict2:
        if(key in dict1):
            if(overwrite):
                d[key] = dict2[key]
            else:
                pass
        else:
            d[key] = dict2[key]
    return(d)

def _comprise(dict1,dict2):
    '''
        dict1 = {'a':1,'b':2,'c':3,'d':4}
        dict2 = {'b':2,'c':3}
        _comprise(dict1,dict2)
    '''
    len_1 = dict1.__len__()
    len_2 = dict2.__len__()
    if(len_2>len_1):
        return(False)
    else:
        for k2 in dict2:
            v2 = dict2[k2]
            if(k2 in dict1):
                v1 = dict1[k2]
                if(v1 == v2):
                    return(True)
                else:
                    return(False)
            else:
                return(False)

#@@@@@@@@@@@@@@@@@@@@
def _update_intersection(dict1,dict2,**kwargs):
    '''
        dict1 = {1:'a',2:'b',3:'c',4:'d'}
        dict2 = {5:'u',2:'v',3:'w',6:'x',7:'y'}
        _update_intersection(dict1,dict2)
        pobj(dict1)
        pobj(dict2)
    '''
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    if(deepcopy == 1):
        dict1 = copy.deepcopy(dict1)
    else:
        pass
    for key in dict2:
        if(key in dict1):
            dict1[key] = dict2[key]
    return(dict1)

def _update(dict1,dict2,**kwargs):
    '''
        dict1 = {1:'a',2:'b',3:'c',4:'d'}
        dict2 = {5:'u',2:'v',3:'w',6:'x',7:'y'}
        _update(dict1,dict2)
        pobj(dict1)
        pobj(dict2)
    '''
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    if(deepcopy == 1):
        dict1 = copy.deepcopy(dict1)
    else:
        pass
    dict1 = _extend(dict1,dict2,overwrite=True,deepcopy=deepcopy)
    return(dict1)

#important and special func
#给elist 添加个类似方法
def _setdefault_via_pathlist(external_dict,path_list,**kwargs):
    '''
        #if path_list already in external_dict, will do nothing
        y = {}
        path_list = ['c','b']
        _setdefault_via_pathlist(y,path_list)
        y
        _setdefault_via_pathlist(y,path_list)
        y = {}
        _setdefault_via_pathlist(y,path_list)
        y
    '''
    if('s2n' in kwargs):
        s2n = kwargs['s2n']
    else:
        s2n = 0
    if('n2s' in kwargs):
        n2s = kwargs['n2s']
    else:
        n2s = 0
    if('default_element' in kwargs):
        default_element = kwargs['default_element']
    else:
        default_element = {}
    this = external_dict
    for i in range(0,path_list.__len__()):
        key = path_list[i]
        if(n2s ==1):
            key = str(key)
        if(s2n==1):
            try:
                int(key)
            except:
                pass
            else:
                key = int(key)
        try:
            this.__getitem__(key)
        except:
            try:
                # necessary ,when default_element = {} or []
                de = copy.deepcopy(default_element)
                this.__setitem__(key,de)
            except:
                return(external_dict)
            else:
                pass
            this = this.__getitem__(key)
        else:
            this = this.__getitem__(key)
    return(external_dict)


#for array_map
def _setdefault_via_pathlist2(path_list,external_dict,**kwargs):
    return(_setdefault_via_pathlist(external_dict,path_list,**kwargs))


def _setitem_via_pathlist(external_dict,path_list,value,**kwargs):
    '''
        y = {'c': {'b': {}}}
        _setitem_via_pathlist(y,['c','b'],200)
    '''
    if('s2n' in kwargs):
        s2n = kwargs['s2n']
    else:
        s2n = 0
    if('n2s' in kwargs):
        n2s = kwargs['n2s']
    else:
        n2s = 0
    this = external_dict
    for i in range(0,path_list.__len__()-1):
        key = path_list[i]
        if(n2s ==1):
            key = str(key)
        if(s2n==1):
            try:
                int(key)
            except:
                pass
            else:
                key = int(key)
        this = this.__getitem__(key)
    this.__setitem__(path_list[-1],value)
    return(external_dict)

#for array_map
def _setitem_via_pathlist2(path_list,external_dict,**kwargs):
    return(_setitem_via_pathlist(external_dict,path_list,**kwargs))



def _getitem_via_pathlist(external_dict,path_list,**kwargs):
    '''
        y = {'c': {'b': 200}}
        _getitem_via_pathlist(y,['c','b'])
    '''
    if('s2n' in kwargs):
        s2n = kwargs['s2n']
    else:
        s2n = 0
    if('n2s' in kwargs):
        n2s = kwargs['n2s']
    else:
        n2s = 0
    this = external_dict
    for i in range(0,path_list.__len__()):
        key = path_list[i]
        if(n2s ==1):
            key = str(key)
        if(s2n==1):
            try:
                int(key)
            except:
                pass
            else:
                key = int(key)
        this = this.__getitem__(key)
    return(this)

#for array_map
def _getitem_via_pathlist2(path_list,external_dict,**kwargs):
    return(_getitem_via_pathlist(external_dict,path_list,**kwargs))


#special 
def _delitem_via_pathlist(external_dict,path_list,**kwargs):
    '''
        y = {'c': {'b': 200}}
        _delitem_via_pathlist(y,['c','b'])
    '''
    if('s2n' in kwargs):
        s2n = kwargs['s2n']
    else:
        s2n = 0
    if('n2s' in kwargs):
        n2s = kwargs['n2s']
    else:
        n2s = 0
    this = external_dict
    for i in range(0,path_list.__len__()-1):
        key = path_list[i]
        if(n2s ==1):
            key = str(key)
        if(s2n==1):
            try:
                int(key)
            except:
                pass
            else:
                key = int(key)
        this = this.__getitem__(key)
    this.__delitem__(path_list[-1])
    return(external_dict)


#for array_map
def _delitem_via_pathlist2(path_list,external_dict,**kwargs):
    return(_delitem_via_pathlist(external_dict,path_list,**kwargs))



def _include_pathlist(external_dict,path_list,**kwargs):
    '''
        y = {
            'a':
                {'x':88},
            'b':
                {
                    'x':
                        {'c':66}
                }
        }
        _include_pathlist(y,['a'])
        _include_pathlist(y,['a','x'])
        _include_pathlist(y,['b','x','c'])
    '''
    if('s2n' in kwargs):
        s2n = kwargs['s2n']
    else:
        s2n = 0
    if('n2s' in kwargs):
        n2s = kwargs['n2s']
    else:
        n2s = 0
    this = external_dict
    for i in range(0,path_list.__len__()):
        key = path_list[i]
        if(n2s ==1):
            key = str(key)
        if(s2n==1):
            try:
                int(key)
            except:
                pass
            else:
                key = int(key)
        try:
            this = this.__getitem__(key)
        except:
            return(False)
        else:
            pass
    return(True)

################

def max_word_width(myDict):
    '''
        currd = {0:'AutoPauseSpeed', 125:'HRLimitLow', 6:'Activity'}
        max_wordwidth(currd)
    '''
    maxValueWidth = 0
    for each in myDict:
        eachValueWidth = myDict[each].__len__()
        if(eachValueWidth > maxValueWidth):
            maxValueWidth = eachValueWidth
    return(maxValueWidth)

def max_display_width(myDict):
    '''
        currd = {0:'你们大家好', 125:'ABCDE', 6:'1234567'}
        dict_get_max_word_displaywidth(currd)
    '''
    maxValueWidth = 0
    for each in myDict:
        eachValueWidth = str_display_width(myDict[each])
        if(eachValueWidth > maxValueWidth):
            maxValueWidth = eachValueWidth
    return(maxValueWidth)


############################
###for nexted

def is_dict(obj):
    '''
        from edict.edict import *
        is_dict({1:2})
        is_dict(200)
    '''
    if(type(obj)==type({})):
        return(True)
    else:
        return(False)

def is_leaf(obj):
    '''
        the below is for nested-dict
        any type is not dict will be treated as a leaf
        empty dict will be treated as a leaf
        from edict.edict import *
        is_leaf(1)
        is_leaf({1:2})
        is_leaf({})
    '''
    if(is_dict(obj)):
        length = obj.__len__()
        if(length == 0):
            return(True)
        else:
            return(False)
    else:
        return(True)

def _gen_sonpl(ele,ppl):
    nppl = copy.deepcopy(ppl)
    nppl.append(ele)
    return(nppl)

def _new_ele_desc():
    '''
    '''
    desc = {
        'leaf':None,
        'depth':None,
        'breadth':None,
        'breadth_path':None,
        'sib_seq':None,
        'path':None,
        'parent_path':None,
        'parent_breadth':None,
        'parent_breadth_path':None,
        'lsib_path':None,
        'rsib_path':None,
        'lcin_path':None,
        'rcin_path':None,
        'sons_count':None,
        'leaf_son_paths':None,
        'non_leaf_son_paths':None,
        'leaf_descendant_paths':None,
        'non_leaf_descendant_paths':None,
        'flat_offset':None,
        'flat_len':None
    }
    return(desc)

def _d2kvmatrix(d):
    '''
        d = {1: 2, 3: {'a': 'b'}}
        km,vm = _d2kvmatrix(d)
        d = {1: {2:{22:222}}, 3: {'a': 'b'}}
        km,vm = _d2kvmatrix(d)
        ##
        km: 按照层次存储pathlist,层次从0开始，
        {
         1: 2,
         3:
            {
             'a': 'b'
            }
        }
        km[0] = [[1],[3]]
        km[1] = [[3,'a']]
        vm: vm比较特殊，不太好理解，请参照函数elel.get_wfs 和_kvmatrix2d
            vm的数组表示层次
        rvmat: 与km对应，存储key对应的value,不过对应层次使km的层次+1
    '''
    km = []
    vm = [list(d.values())]
    vm_history ={0:[0]}
    unhandled = [{'data':d,'kpl':[]}]
    while(unhandled.__len__()>0):
        next_unhandled = []
        keys_level = []
        next_vm_history = {}
        for i in range(0,unhandled.__len__()):
            data = unhandled[i]['data']
            kpl = unhandled[i]['kpl']
            values = list(data.values())
            _setitem_via_pathlist(vm,vm_history[i],values)
            vm_pl = vm_history[i]
            del vm_history[i]
            keys = data.keys()
            keys = elel.array_map(keys,_gen_sonpl,kpl)
            keys_level.extend(keys)
            for j in range(0,values.__len__()):
                v = values[j]
                cond = is_leaf(v)
                if(cond):
                    pass
                else:
                    kpl = copy.deepcopy(keys[j])
                    next_unhandled.append({'data':v,'kpl':kpl})
                    vpl = copy.deepcopy(vm_pl)
                    vpl.append(j)
                    next_vm_history[next_unhandled.__len__()-1] = vpl
        vm_history = next_vm_history
        km.append(keys_level)
        unhandled = next_unhandled
    vm = vm[0]
    return((km,vm))

def show_kmatrix(km):
    '''
        d = {1: {2: {22: 222}}, 3: {'a': 'b'}}
        km = [[[1], [3]], [[1, 2], [3, 'a']], [[1, 2, 22]]]
        show_kmatrix(km)
    '''
    rslt = []
    for i in range(0,km.__len__()):
        level = km[i]
        for j in range(0,level.__len__()):
            kpl = level[j]
            print(kpl)
            rslt.append(kpl)
    return(rslt)

def show_vmatrix(vm):
    '''
        d = {1: {2: {22: 222}}, 3: {'a': 'b'}}
        vm = [[[222]], ['b']]
        show_vmatrix(vm)
    '''
    unhandled = vm
    while(unhandled.__len__()>0):
        next_unhandled = []
        for i in range(0,unhandled.__len__()):
            ele = unhandled[i]
            print(ele)
            cond = elel.is_leaf(ele)
            if(cond):
                pass
            else:
                children = ele[0]
                next_unhandled.append(children)
        unhandled = next_unhandled

def show_kmatrix_as_getStr(km):
    rslt = []
    for i in range(0,km.__len__()):
        level = km[i]
        for j in range(0,level.__len__()):
            kpl = level[j]
            gs = elel.pathlist_to_getStr(kpl)
            print(gs)
            rslt.append(gs)
    return(rslt)


def show_dict(d,l):
    lngth = l.__len__()
    if(type(l[0])== type([])):
        for i in range(0,lngth):
            print(_getitem_via_pathlist(d,l[i]))
    else:
        for i in range(0,lngth):
            pl = elel.gs2pl(l[i])
            print(_getitem_via_pathlist(d,pl))

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def _keypaths(d,*args,**kwargs):
    kdmat = _get_kdmat(d)
    depth = kdmat.__len__()
    if('leaf_only' in kwargs):
        leaf_only = kwargs['leaf_only']
    else:
        leaf_only = False
    if('non_leaf_only' in kwargs):
        non_leaf_only = kwargs['non_leaf_only']
    else:
        non_leaf_only = False
    args_len = args.__len__()
    if(args_len == 0):
        from_lv = 1
        to_lv = depth
    elif(args_len == 1):
        from_lv = args[0]
        to_lv = from_lv+1
    else:
        from_lv = args[0]
        to_lv = args[1]
    rslt = []
    for i in range(from_lv,to_lv):
        klevel = kdmat[i]
        for j in range(0,klevel.__len__()):
            if(leaf_only == True):
                cond = (kdmat[i][j]['leaf'] == True)
            elif(non_leaf_only == True):
                cond = (kdmat[i][j]['leaf'] == False)
            else:
                cond = True
            if(cond):
                rslt.append(kdmat[i][j]['path'])
            else:
                pass
    return(rslt)

##########################################################

def _keys(d,*args,**kwargs):
    kps = _keypaths(d,*args,**kwargs)
    ks = elel.array_map(kps,list.__getitem__,-1)
    return(ks)

##########################################################

def _values(d,*args,**kwargs):
    km,vm = _d2kvmatrix(d)
    rvmat = _get_rvmat(d)
    depth = rvmat.__len__()
    kdmat = _scankm(km)
    if('leaf_only' in kwargs):
        leaf_only = kwargs['leaf_only']
    else:
        leaf_only = False
    if('non_leaf_only' in kwargs):
        non_leaf_only = kwargs['non_leaf_only']
    else:
        non_leaf_only = False
    args_len = args.__len__()
    if(args_len == 0):
        from_lv = 1
        to_lv = depth
    elif(args_len == 1):
        from_lv = args[0]
        to_lv = from_lv+1
    else:
        from_lv = args[0]
        to_lv = args[1]
    rslt = []
    for i in range(from_lv,to_lv):
        rvlevel = rvmat[i]
        for j in range(0,rvlevel.__len__()):
            v = rvlevel[j]
            if(leaf_only == True):
                cond = (kdmat[i][j]['leaf'] == True)
            elif(non_leaf_only == True):
                cond = (kdmat[i][j]['leaf'] == False)
            else:
                cond = True
            if(cond):
                rslt.append(v)
            else:
                pass
    return(rslt)



##########################################################

def _init_descmat_root():
    '''
    '''
    root = _new_ele_desc()
    root['depth'] = 0
    root['leaf'] = False
    root['breadth_path'] =[]
    root['path'] = []
    root['parent_path'] = []
    root['parent_breadth_path'] = []
    return(root)

def _init_descmat_via_km(km,descmat=[]):
    '''
    '''
    ###important to fix strange bug 
    descmat = copy.deepcopy(descmat)
    ###
    descmat_len = descmat.__len__()
    cond = (descmat_len == 0)
    depth = km.__len__()
    for i in range(0,depth):
        klevel = km[i]
        lngth = klevel.__len__()
        dlevel = elel.init(lngth,default_element=_new_ele_desc())
        if(cond):
            descmat.append(dlevel)
        else:
            pass
    descmat = elel.prepend(descmat,[_init_descmat_root()])
    return(descmat)

def _descmat_leaf_handler(desc,pdesc):
    '''
    '''
    desc['leaf_son_paths'] = []
    desc['non_leaf_son_paths'] = []
    desc['leaf_descendant_paths'] = []
    desc['non_leaf_descendant_paths'] = []
    kpl = desc['path']
    ####
    cpkpl = copy.deepcopy(kpl)
    if(pdesc['leaf_son_paths'] == None):
        pdesc['leaf_son_paths'] = [cpkpl]
    else:
        pdesc['leaf_son_paths'].append(cpkpl)
    ####
    if(pdesc['non_leaf_son_paths'] == None):
        pdesc['non_leaf_son_paths'] = []
    else:
        pass
    ####
    cpkpl = copy.deepcopy(kpl)
    if(pdesc['leaf_descendant_paths'] == None):
        pdesc['leaf_descendant_paths'] = [cpkpl]
    else:
        pdesc['leaf_descendant_paths'].append(cpkpl)
    ####
    if(pdesc['non_leaf_descendant_paths'] == None):
        pdesc['non_leaf_descendant_paths'] = []
    else:
        pass

def _descmat_non_leaf_handler(desc,pdesc):
    '''
    '''
    kpl = desc['path']
    ####
    cpkpl = copy.deepcopy(kpl)
    if(pdesc['non_leaf_son_paths'] == None):
        pdesc['non_leaf_son_paths'] = [cpkpl]
    else:
        pdesc['non_leaf_son_paths'].append(cpkpl)
    ####
    if(pdesc['leaf_son_paths'] == None):
        pdesc['leaf_son_paths'] = []
    else:
        pass
    ####
    cpkpl = copy.deepcopy(kpl)
    ldpl = desc['leaf_descendant_paths']
    cpldpl = copy.deepcopy(ldpl)
    nldpl = desc['non_leaf_descendant_paths']
    cpnldpl = copy.deepcopy(nldpl)
    if(pdesc['leaf_descendant_paths'] == None):
        pdesc['leaf_descendant_paths'] = cpldpl
    else:
        pdesc['leaf_descendant_paths'].extend(cpldpl)
    if(pdesc['non_leaf_descendant_paths'] == None):
        pdesc['non_leaf_descendant_paths'] = cpnldpl
        pdesc['non_leaf_descendant_paths'].append(cpkpl)
    else:
        pdesc['non_leaf_descendant_paths'].extend(cpnldpl)
        pdesc['non_leaf_descendant_paths'].append(cpkpl)

def _acc_sons_count(desc):
    if(desc['leaf_son_paths'] == None):
        desc['leaf_son_paths'] = []
    else:
        pass
    if(desc['non_leaf_son_paths'] == None):
        desc['non_leaf_son_paths'] = []
    else:
        pass
    lscnt = desc['leaf_son_paths'].__len__()
    nlscnt = desc['non_leaf_son_paths'].__len__()
    return(lscnt + nlscnt)

def _scankm(km,descmat=[]):
    '''
    '''
    descmat = _init_descmat_via_km(km,descmat=descmat)
    depth = km.__len__()
    klevel = km[depth - 1]
    lngth = klevel.__len__()
    dlevel = descmat[depth]
    pdlevel = descmat[depth-1]
    for j in range(0,lngth):
        kpl = klevel[j]
        desc = dlevel[j]
        desc['leaf'] = True
        desc['depth'] = depth 
        desc['path'] = kpl
        desc['breadth'] = j 
        desc['sons_count'] = 0 
        desc['leaf_son_paths'] = []
        desc['non_leaf_son_paths'] = []
        desc['leaf_descendant_paths'] = []
        desc['non_leaf_descendant_paths'] = []
        pkpl = copy.deepcopy(kpl)
        pkpl.pop(-1)
        desc['parent_path'] = pkpl
        ####
        if(depth < 2):
            pbreadth = 0
        else:
            pbreadth = km[depth-2].index(pkpl)
        #pbreadth = km[depth-2].index(pkpl)
        ####
        desc['parent_breadth'] = pbreadth
        ######
        pdesc = pdlevel[pbreadth]
        _descmat_leaf_handler(desc,pdesc)
    ####
    for i in range(depth-2,0,-1):
        level = i 
        klevel = km[level]
        lngth = klevel.__len__()
        dlevel = descmat[level+1]
        pdlevel = descmat[level]
        for j in range(0,lngth):
            #
            #
            kpl = klevel[j]
            desc = dlevel[j]
            desc['depth'] = level + 1
            desc['path'] = kpl
            desc['breadth'] = j 
            desc['sons_count'] = _acc_sons_count(desc)
            if(desc['sons_count'] == 0):
                desc['leaf'] = True
            else:
                desc['leaf'] = False
            pkpl = copy.deepcopy(kpl)
            pkpl.pop(-1)
            desc['parent_path'] = pkpl
            pbreadth = km[level-1].index(pkpl)
            desc['parent_breadth'] = pbreadth
            ######
            pdesc = pdlevel[pbreadth]
            if(desc['leaf']):
                _descmat_leaf_handler(desc,pdesc)
            else:
                _descmat_non_leaf_handler(desc,pdesc)
    #####depth 1
    level = 0 
    klevel = km[level]
    lngth = klevel.__len__()
    dlevel = descmat[level+1]
    pdlevel = descmat[level]
    for j in range(0,lngth):
        #
        #
        kpl = klevel[j]
        desc = dlevel[j]
        desc['depth'] = level + 1
        desc['path'] = kpl
        desc['breadth'] = j 
        desc['sons_count'] = _acc_sons_count(desc)
        if(desc['sons_count'] == 0):
            desc['leaf'] = True
        else:
            desc['leaf'] = False
        pkpl = copy.deepcopy(kpl)
        pkpl.pop(-1)
        desc['parent_path'] = pkpl
        pdesc = pdlevel[0]
        if(desc['leaf']):
            _descmat_leaf_handler(desc,pdesc)
        else:
            _descmat_non_leaf_handler(desc,pdesc)
    #####root 
    desc = descmat[0][0]
    desc['sons_count'] = _acc_sons_count(desc)
    return(descmat)



def _mat_size(mat):
    '''
    '''
    size = 0
    depth = mat.__len__()
    for i in range(0,depth):
        level = mat[i]
        size = size + level.__len__()
    return(size)


def _mat_max_width(mat):
    widths = elel.array_map(mat,len)
    return(max(widths))


#km 是一个广度优先的pathlist 存储二维矩阵
#vm 是一个嵌套List
#ltree = elel.ListTree(vm) 
#ltree.tree() 是一个深度优先的 pathlist 一维数组 
#_mat_size(km) == ltree.tree().__len__()
#ltree.desc[0][0] 是根节点 
#km[i] 与 ltree.desc[i-1] 对应
#

def get_kmwfs(km):
    '''
    '''
    kmwfs = []
    for i in range(0,km.__len__()):
        level = km[i]
        for j in range(0,level.__len__()):
            kpl = level[j]
            kmwfs.append(kpl)
    return(kmwfs)

def get_kmdfs(km,vmwfs):
    '''
    '''
    kmwfs = get_kmwfs(km)
    kmdfs = elel.batsorted(vmwfs,kmwfs)[0]
    return(kmdfs)
    


#
def _scanvm(vm):
    ltree = elel.ListTree(vm)
    vdescmat = ltree.desc
    return(vdescmat)


#
def _scan(d):
    '''
    '''
    km,vm = _d2kvmatrix(d)
    kdescmat = _scankm(km)
    vdescmat = _scanvm(vm)
    return((kdescmat,vdescmat))


def _kvmatrix2d(km,vm):
    '''
        
        km = [[[1], [3]], [[1, 2], [3, 'a']], [[1, 2, 22]]]
        show_kmatrix(km)
        vm = [[[222]], ['b']]
        show_vmatrix(vm)
        
        d = _kvmatrix2d(km,vm)
    '''
    d = {}
    kmwfs = get_kmwfs(km)
    vmwfs = elel.get_wfs(vm)
    lngth = vmwfs.__len__()
    for i in range(0,lngth):
        value = elel.getitem_via_pathlist(vm,vmwfs[i])
        cond = elel.is_leaf(value)
        if(cond):
            _setitem_via_pathlist(d,kmwfs[i],value)
        else:
            _setdefault_via_pathlist(d,kmwfs[i])
    return(d)


def kmdfs_cond_func(ele,d,from_lv,to_lv,leaf_only,non_leaf_only):
    cond1 = (ele.__len__() >= from_lv)
    cond2 = (ele.__len__() <= to_lv)
    value = _getitem_via_pathlist(d,ele)
    leaf = is_leaf(value)
    if(leaf_only):
        cond3 = (leaf == True)
    elif(non_leaf_only):
        cond3 = (leaf == False)
    else:
        cond3 = True
    cond = (cond1 & cond2 & cond3)
    return(cond)



def _get_rvwfs(d):
    km,vm = _d2kvmatrix(d)
    kmwfs = get_kmwfs(km)
    rvwfs = elel.array_map(kmwfs,_getitem_via_pathlist2,d)
    return(rvwfs)

def _get_rvdfs(d):
    km,vm = _d2kvmatrix(d)
    vmwfs = elel.get_wfs(vm)
    kmdfs = get_kmdfs(km,vmwfs)
    rvdfs = elel.array_map(kmdfs,_getitem_via_pathlist2,d)
    return(rvdfs)


def _get_rvmat(d):
    '''
        d = {
         'x':
              {
               'x2': 'x22',
               'x1': 'x11'
              },
         'y':
              {
               'y1': 'v1',
               'y2':
                     {
                      'y4': 'v4',
                      'y3': 'v3'
                     }
              },
         't': 20,
         'u':
              {
               'u1': 'u2'
              }
        }
        
        
    '''
    km,vm = _d2kvmatrix(d)
    def map_func(ele,indexc,indexr):
        return(_getitem_via_pathlist(d,ele))
    rvmat = elel.matrix_map(km,map_func)
    rvmat = elel.prepend(rvmat,[])
    return(rvmat)

#######################

def _cond_select_key(d,cond_ele,*args,**kwargs):
    '''
    '''
    if('mode' in kwargs):
        mode = kwargs['mode']
    else:
        mode = 'loose'
    kdfs = _get_kdfs(d)
    t = type(cond_ele)
    if(t == type('')):
        if(mode == 'loose'):
            rslt = elel.select_loose_in(kdfs,cond_ele)
        else:
            rslt = elel.select_strict_in(kdfs,cond_ele)
    elif(t == type(re.compile(''))):
        rslt = elel.select_regex_in(kdfs,cond_ele)
    elif(t == type(lambda x:x)):
        cond_func = cond_ele
        if('cond_func_args' in kwargs):
            cond_func_args = kwargs['cond_func_args']
        else:
            cond_func_args = []
        rslt = elel.cond_select_values_all2(kdfs,cond_func=cond_func, cond_func_args = cond_func_args)
    else:
        rslt = kdfs
    return(rslt)

#######################

def get_kdmat_loc(kdmat,keypath):
    lngth = keypath.__len__()
    level = kdmat[lngth]
    def cond_func(ele,keypath):
        cond = (ele['path'] == keypath)
        return(cond)
    index = elel.cond_select_indexes_all(level,cond_func=cond_func,cond_func_args =[keypath])[0]
    return((lngth,index))

#######################

def get_vndmat_attr(d,keypath,attr,**kwargs):
    '''
        get_vndmat_attr(d,['x'],'lsib_path',path2keypath=True)
        get_vndmat_attr(d,['t'],'lsib_path',path2keypath=True)
        get_vndmat_attr(d,['u'],'lsib_path',path2keypath=True)
        get_vndmat_attr(d,['y'],'lsib_path',path2keypath=True)
    '''
    kt,vn = _d2kvmatrix(d)
    kdmat = _scankm(kt)
    ltree = elel.ListTree(vn)
    vndmat = ltree.desc
    loc = get_kdmat_loc(kdmat,keypath)
    rslt = vndmat[loc[0]][loc[1]][attr]
    if(rslt == None):
        pass
    elif(elel.is_matrix(rslt,mode='loose')):
        if('path2loc' in kwargs):
            rslt = elel.array_map(rslt,ltree.path2loc)
        else:
            pass
        if('path2keypath' in kwargs):
            nlocs = elel.array_map(rslt,ltree.path2loc)
            def cond_func(ele,kdmat):
                return(kdmat[ele[0]][ele[1]]['path'])
            rslt = elel.array_map(nlocs,cond_func,kdmat)
        else:
            pass        
    else:
        if('path2loc' in kwargs):
            rslt = ltree.path2loc(rslt)
        else:
            pass
        if('path2keypath' in kwargs):
            nloc = ltree.path2loc(rslt)
            rslt = kdmat[nloc[0]][nloc[1]]['path']
        else:
            pass
    return(rslt)


######################
#refer to elist APIs for next development 
######################

class Edict():
    '''
        ed =Edict(bigd)
    '''
    def __init__(self,*args,**kwargs):
        '''
            ed =Edict(bigd)
        '''
        lngth = args.__len__()
        if(lngth == 1):
            self.dict = args[0]
        else:
            kl = args[0]
            vl = args[1]
            self.dict = kvlist2d(kl,vl)
    def sort_via_key(self,**kwargs):
        nd = _sort_via_key(self.dict,**kwargs)
        return(Edict(nd))
    def sort_via_value(self,**kwargs):
        nd = _sort_via_value(self.dict,**kwargs)
        return(Edict(nd))
    def sort_via_cond(self,**kwargs):
        nd = _cond_sort(self.dict,**kwargs)
        return(Edict(nd))
    def reorder_via_vlist(self,nvl,**kwargs):
        nd = _reorder_via_vlist(self.dict,nvl,**kwargs)
        return(Edict(nd))
    def reorder_via_klist(self,nkl,**kwargs):
        nd = _reorder_via_klist(self.dict,nkl,**kwargs)
        return(Edict(nd))
    ####
    def sub_via_value(self,*vs,**kwargs):
        '''
            d= {1:'a',2:'b',3:'a',4:'d',5:'e'}
            ed = eded.Edict(d)
            ed.sub_via_value('a','d')
        '''
        sd = _select_norecur_via_value(self.dict,*vs,**kwargs)
        return(Edict(sd))
    def sub(self,*ks,**kwargs):
        sd = _select_norecur(self.dict,*ks,**kwargs)
        return(Edict(sd))
    def klist(self):
        kl,vl = d2kvlist(self.dict)
        return(kl)
    def vlist(self):
        kl,vl = d2kvlist(self.dict)
        return(vl)
    def kvlists(self):
        return(d2kvlist(self.dict))
    def ktree(self):
        tr,nest = _d2kvmatrix(self.dict)
        return(tr)
    def vnest(self):
        tr,nest = _d2kvmatrix(self.dict)
        return(nest)
    def ktree_vnest(self):
        return(_d2kvmatrix(self.dict))
    def kwfs(self):
        tr,nest = _d2kvmatrix(self.dict)
        rslt = get_kmwfs(tr)
        return(rslt)
    def vwfs(self):
        tr,nest = _d2kvmatrix(self.dict)
        rslt = elel.get_wfs(nest)
        return(rslt)
    def rvwfs(self):
        return(_get_rvwfs(self.dict))
    def wfses(self):
        return(_d2kvmatrix(self.dict))
    def kdfs(self):
        tr,nest = _d2kvmatrix(self.dict)
        vwfs1 = elel.get_wfs(nest)
        rslt = get_kmdfs(tr,vwfs1)
        return(rslt)
    def vdfs(self):
        tr,nest = _d2kvmatrix(self.dict)
        vwfs1 = elel.get_wfs(nest)
        rslt = elel.wfs2dfs(vwfs1)
        return(rslt)
    def rvdfs(self):
        return(_get_rvdfs(self.dict))
    def dfses(self):
        return((self.kdfs(),self.vdfs()))
    def kdmat(self):
        return(_get_kdmat(self.dict))
    def vndmat(self):
        return(_get_vndmat(self.dict))
    def ktvndmats(self):
        return(_scan(self.dict))
    def kpmat(self):
        return(_get_kpmat(self.dict))
    def rvmat(self):
        return(_get_rvmat(self.dict))
    def include_pathlist(self,*args,**kwargs):
        cond = _include_pathlist(self.dict,list(args),**kwargs)
        return(cond)
    def pathlists(self):
        tr = self.ktree()
        pls = show_kmatrix(tr)
        return(pls)
    def bracket_lists(self):
        tr = self.ktree()
        brls = show_kmatrix_as_getStr(tr)
        return(brls)
    def __repr__(self):
        tr = self.ktree()
        show_kmatrix_as_getStr(tr)
        return(self.dict.__repr__())
    def __str__(self):
        return(self.dict.__str__())
    def __getitem__(self,*args,**kwargs):
        #very special in __getitem__
        if(isinstance(args[0],tuple)):
            #very special in __getitem__
            pl = list(args[0])
        else:
            #very special in __getitem__
            pl = list(args)
        return(_getitem_via_pathlist(self.dict,pl))
    def cond_select_key(self,cond_ele,*args,**kwargs):
        return(_cond_select_key(self.dict,cond_ele,*args,**kwargs))
    def cond_select_leaf_value(self,cond_ele,*args,**kwargs):
        return(_cond_select_leaf_value(self.dict,cond_ele,*args,**kwargs))
    def cond_select_keypath(self,keypath,*args,**kwargs):
        return(_cond_select_keypath(self.dict,keypath,*args,**kwargs))
    def __setitem__(self,*args,**kwargs):
        #very special in __setitem__
        if(isinstance(args[0],tuple)):
            #very special in __getitem__
            pl = list(args[0])
            value = args[1]
        else:
            #very special in __getitem__
            pl = [args[0]]
            value = args[1]
        return(_setitem_via_pathlist(self.dict,pl,value))
    def setdefault(self,*args,**kwargs):
        '''
        '''
        return(_setdefault_via_pathlist(self.dict,list(args)))
    def __delitem__(self,*args,**kwargs):
        #very special in __getitem__
        if(isinstance(args[0],tuple)):
            #very special in __getitem__
            pl = list(args[0])
        else:
            #very special in __getitem__
            pl = list(args)
        return(_delitem_via_pathlist(self.dict,pl))
    def keys_via_value(self,value,**kwargs):
        return(_keys_via_value(self.dict,value,**kwargs))
    def pathlists_via_value(self,value,**kwargs):
        return(_keys_via_value(self.dict,value,**kwargs))
    def bracket_lists_via_value(self,value,**kwargs):
        return(_bracket_lists_via_value(self.dict,value,**kwargs))
    def vksdesc(self):
        return(_vksdesc(self.dict))
    def contains(self,value,**kwargs):
        return(_contains(self.dict,value,**kwargs))
    def count(self,value,**kwargs):
        return(_count(self.dict,value,**kwargs))
    def keypaths(self,*args,**kwargs):
        return(_keypaths(self.dict,*args,**kwargs))
    def keys(self,*args,**kwargs):
        return(_keys(self.dict,*args,**kwargs))
    def values(self,*args,**kwargs):
        return(_values(self.dict,*args,**kwargs))
    def depth(self,**kwargs):
        kt,vn = _d2kvmatrix(self.dict)
        dpth = kt.__len__()
        return(dpth)
    def total(self,**kwargs):
        kt,vn = _d2kvmatrix(self.dict)
        size = _mat_size(kt)
        return(size)
    def maxLevelWidth(self,**kwargs):
        kt,vn = _d2kvmatrix(self.dict)
        mxwdth = _mat_max_width(kt)
        return(mxwdth)
    def flatWidth(self,**kwargs):
        kt,vn = _d2kvmatrix(self.dict)
        ltree = elel.ListTree(vn)
        fwdth = ltree.flatWidth
        return(fwdth)
    def tree(self,**kwargs):
        dpth = self.depth()
        if('leaf_only' in kwargs):
            leaf_only = kwargs['leaf_only']
        else:
            leaf_only = False
        if('non_leaf_only' in kwargs):
            non_leaf_only = kwargs['non_leaf_only']
        else:
            non_leaf_only = False
        if('from_lv' in kwargs):
            from_lv = kwargs['from_lv']
        else:
            from_lv = 1
        if('to_lv' in kwargs):
            to_lv = kwargs['to_lv']
        else:
            to_lv = dpth
        if('show' in kwargs):
            show = kwargs['show']
        else:
            show = True
        kmdfs = self.kdfs()
        tr = elel.filter(kmdfs,kmdfs_cond_func,self.dict,from_lv,to_lv,leaf_only,non_leaf_only)
        if(show):
            elel.forEach(tr,print)
        else:
            pass
        return(tr)
    def ancestor_keypaths(self,keypath):
        cond = _include_pathlist(self.dict,keypath) 
        if(cond):
            akps = _ancestor_keypaths(keypath)
            return(akps)
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def ancestors(self,keypath):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            ans = _ancestors(self.dict,keypath)
            return(ans)
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def parent_keypath(self,keypath):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            pkp = keypath[:-1]
            return(pkp)
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def parent(self,keypath):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            pkp = keypath[:-1]
            v = _getitem_via_pathlist(self.dict,pkp)
            return(v)
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def descendant_keypaths(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            return(_descendant_keypaths(self.dict,keypath,**kwargs))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def descendants(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            return(_descendants(self.dict,keypath,**kwargs))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def prevSibPath(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            return(get_vndmat_attr(self.dict,keypath,'lsib_path',path2keypath=True))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def prevSibling(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            pl = get_vndmat_attr(self.dict,keypath,'lsib_path',path2keypath=True)
            return(_getitem_via_pathlist(self.dict,pl))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def lsib_path(self,keypath,**kwargs):
        return(self.prevSibPath(keypath,**kwargs))
    def lsib(self,keypath,**kwargs):
        return(self.prevSibling(keypath,**kwargs))
    def nextSibPath(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            return(get_vndmat_attr(self.dict,keypath,'rsib_path',path2keypath=True))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def nextSibling(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            pl = get_vndmat_attr(self.dict,keypath,'rsib_path',path2keypath=True)
            return(_getitem_via_pathlist(self.dict,pl))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def rsib_path(self,keypath,**kwargs):
        return(self.nextSibPath(keypath,**kwargs))
    def rsib(self,keypath,**kwargs):
        return(self.nextSibling(keypath,**kwargs))
    def lcin_path(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            return(get_vndmat_attr(self.dict,keypath,'lcin_path',path2keypath=True))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def lcin(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            pl = get_vndmat_attr(self.dict,keypath,'lcin_path',path2keypath=True)
            return(_getitem_via_pathlist(self.dict,pl))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def rcin_path(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            return(get_vndmat_attr(self.dict,keypath,'rcin_path',path2keypath=True))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def rcin(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            pl = get_vndmat_attr(self.dict,keypath,'rcin_path',path2keypath=True)
            return(_getitem_via_pathlist(self.dict,pl))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    ######################################################################################
    def sons(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            lpl = get_vndmat_attr(self.dict,keypath,'leaf_son_paths',path2keypath=True)
            lpl = copy.deepcopy(lpl)
            nlpl = get_vndmat_attr(self.dict,keypath,'non_leaf_son_paths',path2keypath=True)
            nlpl = copy.deepcopy(nlpl)
            if('leaf_only' in kwargs):
                return(elel.array_map(lpl,_getitem_via_pathlist2,self.dict))
            elif('non_leaf_only' in kwargs):
                return(elel.array_map(nlpl,_getitem_via_pathlist2,self.dict))
            else:
                lpl.extend(nlpl)
                return(elel.array_map(lpl,_getitem_via_pathlist2,self.dict))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def son_paths(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            lpl = get_vndmat_attr(self.dict,keypath,'leaf_son_paths',path2keypath=True)
            lpl = copy.deepcopy(lpl)
            nlpl = get_vndmat_attr(self.dict,keypath,'non_leaf_son_paths',path2keypath=True)
            nlpl = copy.deepcopy(nlpl)
            if('leaf_only' in kwargs):
                return(pl)
            elif('non_leaf_only' in kwargs):
                return(nlpl)
            else:
                lpl.extend(nlpl)
                return(lpl)
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def sib_paths(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            rslt = _get_sib_paths(self.dict,keypath,**kwargs)
            return(rslt)
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def sibs(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            sibpls = _get_sib_paths(self.dict,keypath,**kwargs)
            return(elel.array_map(sibpls,_getitem_via_pathlist2,self.dict))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    ######################################################################################
    def precedingSibPaths(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            sibpls = _get_sib_paths(self.dict,keypath,**kwargs)
            index = sibpls.index(keypath)
            sibpls = sibpls[:index] 
            return(sibpls)
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def precedingSibs(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            sibpls = _get_sib_paths(self.dict,keypath,**kwargs)
            index = sibpls.index(keypath)
            sibpls = sibpls[:index]
            return(elel.array_map(sibpls,_getitem_via_pathlist2,self.dict))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def preceding_sib_paths(self,keypath,**kwargs):
        return(self.precedingSibPaths(keypath,**kwargs))
    def preceding_sibs(self,keypath,**kwargs):
        return(self.precedingSibs(keypath,**kwargs))
    ######################################################################################
    def followingSibPaths(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            sibpls = _get_sib_paths(self.dict,keypath,**kwargs)
            index = sibpls.index(keypath)
            sibpls = sibpls[(index+1):]
            return(sibpls)
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def followingSibs(self,keypath,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            sibpls = _get_sib_paths(self.dict,keypath,**kwargs)
            index = sibpls.index(keypath)
            sibpls = sibpls[(index+1):]
            return(elel.array_map(sibpls,_getitem_via_pathlist2,self.dict))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def following_sib_paths(self,keypath,**kwargs):
        return(self.followingSibPaths(keypath,**kwargs))
    def following_sibs(self,keypath,**kwargs):
        return(self.followingSibs(keypath,**kwargs))
    ######################################################################################
    def some_sib_paths(self,keypath,*args,**kwargs):
        args = list(args)
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            rslt = _get_sib_paths(self.dict,keypath,**kwargs)
            rslt = elel.select_seqs(rslt,args)
            return(rslt)
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def some_sibs(self,keypath,*args,**kwargs):
        args = list(args)
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            sibpls = _get_sib_paths(self.dict,keypath,**kwargs)
            sibpls = elel.select_seqs(sibpls,args)
            return(elel.array_map(sibpls,_getitem_via_pathlist2,self.dict))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def someSibPaths(self,keypath,*args,**kwargs):
        return(self.some_sib_paths(keypath,*args,**kwargs))
    def someSibs(self,keypath,*args,**kwargs):
        return(self.some_sibs(keypath,*args,**kwargs))
    ######################################################################################
    def which_sib_path(self,keypath,which,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            sibpls = _get_sib_paths(self.dict,keypath,**kwargs)
            which = sibpls[which]
            return(which)
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def which_sib(self,keypath,which,**kwargs):
        cond = _include_pathlist(self.dict,keypath)
        if(cond):
            sibpls = _get_sib_paths(self.dict,keypath,**kwargs)
            which = sibpls[which]
            return(_getitem_via_pathlist(self.dict,which))
        else:
            print('keypath: {0} not in '.format(keypath))
            return(None)
    def whichSibPaths(self,keypath,which,**kwargs):
        return(self.which_sib_path(keypath,which,**kwargs))
    def whichSib(self,keypath,which,**kwargs):
        return(self.which_sib(keypath,which,**kwargs))   
    ######################################################################################
    def tlist(self):
        return(dict2tlist(self.dict))
    def mirrable(self):
        return(is_mirrable(self.dict))
    def mirror(self,**kwargs):
        md = dict_mirror(self.dict,**kwargs)
        return(md)
    def union(self,ed2,**kwargs):
        d3 = _union(self.dict,ed2.dict)
        return(Edict(d3))
    def diff(self,ed2,**kwargs):
        d3 = _diff(self.dict,ed2.dict)
        return(Edict(d3))
    def intersection(self,ed2,**kwargs):
        d3 = _intersection(self.dict,ed2.dict)
        return(Edict(d3))
    def complement(self,ed2,**kwargs):
        d3 = _complement(self.dict,ed2.dict)
        return(Edict(d3))
    def uniqualize(self,**kwargs):
        if('deepcopy' in kwargs):
            deepcopy = kwargs['deepcopy']
        else:
            deepcopy = 0
        d3 = _uniqualize(self.dict)
        if(deepcopy):
            pass
        else:
            self.dict = d3
        return(Edict(d3))
    def extend(self,ed2,**kwargs):
        if('deepcopy' in kwargs):
            deepcopy = kwargs['deepcopy']
        else:
            deepcopy = 0
        d3 = _extend(self.dict,ed2.dict,**kwargs)
        if(deepcopy):
            pass
        else:
            self.dict = d3
        return(Edict(d3))
    def comprise(self,ed2,**kwargs):
        cond = _comprise(self.dict,ed2.dict)
        return(cond)
    def update_intersection(self,ed2,**kwargs):
        if('deepcopy' in kwargs):
            deepcopy = kwargs['deepcopy']
        else:
            deepcopy = 0
        d3 = _update_intersection(self.dict,ed2.dict,**kwargs)
        if(deepcopy):
            pass
        else:
            self.dict = d3
        return(Edict(d3))
    def update(self,ed2,**kwargs):
        if('deepcopy' in kwargs):
            deepcopy = kwargs['deepcopy']
        else:
            deepcopy = 0
        d3 = _update(self.dict,ed2.dict,**kwargs)
        if(deepcopy):
            pass
        else:
            self.dict = d3
        return(Edict(d3))
    #################################
    #################################
    
#ktree 
#vnest 



#


def get_matloc_mapping(ktree,vdmat,attrname):
    kvm = {}
    vkm = {}
    for i in range(0,ktree.__len__()):
        klevel = ktree[i]
        vlevel = vdmat[i+1]
        for j in range(0,klevel.__len__()):
            k = tuple(klevel[j])
            v = tuple(vlevel[j][attrname])
            kvm[k] = v
            vkm[v] = k
    return((kvm,vkm))

def get_ktree_loc(ktree,kpath):
    lngth = kpath.__len__()
    level = lngth - 1
    klevel = ktree[level]
    index = klevel.index(kpath)
    return((level,index))

def ktrloc2vdloc(loc):
    return((loc[0]+1,loc[1]))

def vdloc2ktrloc(loc):
    return((loc[0]-1,loc[1]))

def get_attr_via_kpath_from_vdmat(vdmat,attrname,ktree,kpath):
    loc = get_ktree_loc(ktree,kpath)
    loc = ktrloc2vdloc(loc)
    return(vdmat[loc[0]][loc[1]][attrname])


#for checking 

class DictTree():
    '''
        dtree = DictTree(bigd)
    '''
    def __init__(self,*args,**kwargs):
        lngth = args.__len__()
        if(lngth == 1):
            self.dict = args[0]
            self.klist,self.vlist = d2kvlist(self.dict)
        else:
            self.klist = args[0]
            self.vlist = args[1]
            self.dict = kvlist2d(self.klist,self.vlist)
        self.ktree,self.vnest = _d2kvmatrix(self.dict)
        self.kwfs = get_kmwfs(self.ktree)
        self.vwfs = elel.get_wfs(self.vnest)
        self.kdfs = get_kmdfs(self.ktree,self.vwfs)
        self.vdfs = elel.wfs2dfs(self.vwfs)
        self.depth = self.ktree.__len__()
        self.kdescmat,self.vdescmat = _scan(self.dict)
    def __repr__(self):
        show_kmatrix_as_getStr(self.ktree)
        return(self.dict.__repr__())
    def tree(self,**kwargs):
        if('leaf_only' in kwargs):
            leaf_only = kwargs['leaf_only']
        else:
            leaf_only = False
        if('non_leaf_only' in kwargs):
            non_leaf_only = kwargs['non_leaf_only']
        else:
            non_leaf_only = False
        if('from_lv' in kwargs):
            from_lv = kwargs['from_lv']
        else:
            from_lv = 1
        if('to_lv' in kwargs):
            to_lv = kwargs['to_lv']
        else:
            to_lv = self.depth
        if('show' in kwargs):
            show = kwargs['show']
        else:
            show = True
        tr = elel.filter(kmdfs,kmdfs_cond_func,self.dict,from_lv,to_lv,leaf_only,non_leaf_only)
        if(show):
            elel.forEach(tr,print)
        else:
            pass
        return(tr)
    ####




##########################

def sub_some(d,*args,**kwargs):
    kl = list(args)
    nd = sub_algo(d,kl,**kwargs)
    return(nd)


def sub_not_some(d,*args,**kwargs):
    kl = list(args)
    nd = sub_not_algo(d,kl,**kwargs)
    return(nd)


def sub_algo(d,kl,**kwargs):
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = True
    if(deepcopy):
        nd = copy.deepcopy(d)
    else:
        nd = d
    nnd = {}
    for k in kl:
        if(k in nd):
            nnd[k] = nd[k]
        else:
            pass
    return(nnd)


def sub_not_algo(d,kl,**kwargs):
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = True
    if(deepcopy):
        nd = copy.deepcopy(d)
    else:
        nd = d
    full_kl = list(d.keys())
    nnd = {}
    for k in full_kl:
        if(not(k in kl)):
            nnd[k] = nd[k]
        else:
            pass
    return(nnd)




def sub_value_some(d,*args,**kwargs):
    vl = list(args)
    nd = sub_value_algo(d,vl,**kwargs)
    return(nd)

def sub_value_algo(d,vl,**kwargs):
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = True
    if(deepcopy):
        nd = copy.deepcopy(d)
    else:
        nd = d
    nnd = {}
    kl = list(d.keys())
    for k in kl:
        v = nd[k]
        if(v in vl):
            nnd[k] = nd[k]
        else:
            pass
    return(nnd)




def str_key_fuzzy(d,k):
    arr = list(d.keys())
    kl = elel.str_fuzzy_search(arr,k)
    nd = sub_algo(d,kl)
    return(nd)


def str_value_fuzzy(d,v):
    arr = list(d.values())
    vl = elel.str_fuzzy_search(arr,v)
    nd = sub_value_algo(d,vl)
    return(nd)



def str_fuzzy(d,korv):
    ndk = str_key_fuzzy(d,korv)
    ndv = str_value_fuzzy(d,korv)
    nd = _union(ndk,ndv)
    #pobj(nd)
    return(nd)
####################################

#####################
#json 会把数字key值如1, 变成'1'

def intize(ns):
    try:
        n = int(ns)
    except:
        return(ns)
    else:
        return(n)

def intize_json(js):
    kpmat = _get_kpmat(js)
    ncache = {}
    for i in range(0,kpmat.__len__()):
        row = kpmat[i]
        lngth = row.__len__()
        for j in range(0,lngth):
            pl = row[j]
            v =  _getitem_via_pathlist(js,pl)
            npl = elel.array_map(pl,intize)
            if(is_leaf(v)):
                _setdefault_via_pathlist(ncache,npl)
                _setitem_via_pathlist(ncache,npl,v)
            else:
                pass
    return(ncache)


#####################


def mapkvV(d,map_func,*map_func_other_args,**kwargs):
    nd = copy.deepcopy(d)
    for k in d:
        v = d[k]
        nd[k] = map_func(k,v,*map_func_other_args)
    return(nd)

def mapkvK(d,map_func,*map_func_other_args,**kwargs):
    nd = copy.deepcopy(d)
    for k in d:
        v=d[k]
        k = map_func(k,v,*map_func_other_args)
        nd[k] = v
    return(nd)


def mapvV(d,map_func,*map_func_other_args,**kwargs):
    nd = copy.deepcopy(d)
    for k in d:
        v = d[k]
        nd[k] = map_func(v,*map_func_other_args)
    return(nd)

def mapvK(d,map_func,*map_func_other_args,**kwargs):
    nd = copy.deepcopy(d)
    for k in d:
        v=d[k]
        k = map_func(v,*map_func_other_args)
        nd[k] = v
    return(nd)

def mapkV(d,map_func,*map_func_other_args,**kwargs):
    nd = copy.deepcopy(d)
    for k in d:
        v = d[k]
        nd[k] = map_func(k,*map_func_other_args)
    return(nd)

def mapkK(d,map_func,*map_func_other_args,**kwargs):
    nd = copy.deepcopy(d)
    for k in d:
        v=d[k]
        k = map_func(k,*map_func_other_args)
        nd[k] = v
    return(nd)


#
def slctvlKL(d,kl,**kwargs):
    if("deepcopy" in kwargs):
        pass
    else:
        d = copy.deepcopy(d)
    vl = []
    for i in range(len(kl)):
        k = kl[i]
        v = d[k]
        vl.append(v)
    return(vl)


#
def kv_forof_l(d,map_func,*args):
    rslt = []
    for k in d:
        v = d[k]
        ele = map_func(k,v,*args)
        rslt.append(ele)
    return(rslt)


######
######


def get_own_visible_attrs(obj):
    '''
        >>> class tst():
        ...     def __init__(self):
        ...         self._u = "_u"
        ...         self.u = "u"
        ...
        >>> t = tst()
        >>>
        >>> get_own_visible_attrs(t)
        ['u']
        >>>
    '''
    attrs = get_own_attrs(obj)
    attrs = elel.cond_select_values_all(attrs,cond_func=lambda ele:not(ele.startswith("_")))
    return(attrs)


class _Orb():
    pass


def d2orb(d):
    orb = _Orb()
    for k in d:
        orb.k = d[k]
    return(orb)

def orb2d(orb):
    attrs = get_all_visible_attrs(orb)
    d = {}
    for attr in attrs:
        d[attr] = orb.__getattribute__(attr)
    return(d)
