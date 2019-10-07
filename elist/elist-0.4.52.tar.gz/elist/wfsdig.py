from edict.edict import kvlist2d,d2kvlist
import copy

def _init_ele(*args):
    if(args.__len__()==1):
        d = args[0]
    else:
        kl = args[0]
        vl = args[1]
        d = kvlist2d(kl,vl)
    return(d)

def _init_shared(*args):
    d = _init_ele(*args)
    return(d)

def _init_root(*args):
    d = _init_ele(*args)
    d["_pbreadth"] = None
    d["_breadth"] = 0
    d["_depth"] = 0
    d["_bpl"] = [0]
    d["_children"] = []
    return(d)

def _dcd(kl,vl):
    d = kvlist2d(kl,vl)
    return(d)

def _encd(d,kl):
    vl = []
    for i in range(kl.__len__()):
        k = kl[i]
        vl.append(d[k])
    return(vl)

def _init_unhandled(root,dmat):
    root = _init_root(root)
    unhandled = [root]
    dmat.append(unhandled)
    return((unhandled,dmat))


def _append_pl(pl,tag):
    npl = copy.deepcopy(pl)
    npl.append(tag)
    return(npl)


def _gen(unhandled,shared,get_children,dmat):
    while(unhandled.__len__()>0):
        next_unhandled = []
        next_depth = len(dmat)
        for i in range(unhandled.__len__()):
            ele = unhandled[i]
            pbreadth = i
            base_breadth = len(next_unhandled)
            children = get_children(ele,shared)
            for j in range(len(children)):
                child = children[j]
                child["_pbreadth"] = pbreadth
                child["_breadth"] = base_breadth + j
                child["_depth"] = next_depth
                child["_bpl"] = _append_pl(ele["_bpl"],child["_breadth"])
                child["_children"] = []
                ele["_children"].append((child["_depth"],child["_breadth"]))
            next_unhandled.extend(children)
        unhandled = next_unhandled
        dmat.append(unhandled)
        yield(unhandled)
        yield(shared)
    


class DIG():
    def __init__(self,**kwargs):
        self.dmat = []
        if("shared" in kwargs):
            self.shared = kwargs["shared"]
        else:
            if("shared_kl" in kwargs):
                shared_kl = kwargs["shared_kl"]
            else:
                shared_kl = None
            if("shared_vl" in kwargs):
                shared_vl = kwargs["shared_vl"]
            else:
                shared_vl = None
            self.shared = _init_shared(shared_kl,shared_vl)
        if("root" in kwargs):
            self.root = kwargs["root"]
            self.ele_kl,self.root_vl  = d2kvlist(self.root)
        else:
            ele_kl = kwargs["ele_kl"]
            root_vl = kwargs["root_vl"]
            self.root = kvlist2d(self.ele_kl,self.root_vl)
        self.unhandled,self.dmat= _init_unhandled(self.root,self.dmat)
        self.get_children = kwargs['get_children']
        self.gen = _gen(self.unhandled,self.shared,self.get_children,self.dmat)
    def next(self):
        return(self.gen.__next__())
    def final(self):
        for it in self.gen:
            pass
        if(len(self.dmat[-1])==0):
            del self.dmat[-1]
        else:
            pass
        return((self.shared,self.dmat))
    @classmethod
    def dcd(cls,kl,vl):
        return(_dcd(kl,vl))


######################################################################################
#在已经填充children的情况下

def _wfs_b2t_traverse(dmat,func,**kwargs):
    '''
    '''
    if("cond_func" in kwargs):
        cond_func = kwargs['cond_func']
    else:
        cond_func = lambda ele:True
    depth = len(dmat)
    for i in range(depth-1,0,-1):
        layer = dmat[i]
        breadth = len(layer)
        for j in range(breadth):
            ele = layer[j]
            cond = cond_func(ele)
            ele =  func(ele) if(cond) else ele
            dmat[i][j] = ele
    return(dmat)


def _is_leaf(ele):
    return(len(ele['_children']) == 0)

def _is_non_leaf(ele):
    return(len(ele['_children']) != 0)

def _wfs_b2t_traverse_leaf(dmat,func):
    return(_wfs_b2t_traverse(dmat,func,cond_func=_is_leaf))

def _wfs_b2t_traverse_non_leaf(dmat,func):
    return(_wfs_b2t_traverse(dmat,func,cond_func=_is_non_leaf))



######################################################################################

def help(k):
    if(k == "ele"):
        print("ele must be a dict")
        print("root,ele ahave the same format")
        print("keys of ele : ele_kl")
    elif(k == "shared"):
        print("shared must be a dict")
        print("shared is used to store common structure for update")
        print("keys of shared : shared_kl")
        print("values of shared : shared_vl")
    elif(k == "root"):
        print("root must be a dict")
        print("root,ele ahave the same format")
        print("keys of root : ele_kl")
        print("values of root: root_vl")
    elif(k == "get_children"):
        print("get_children must be a function")
        print(":param dict ele")
        print(":param dict shared")
        print(":return list: the returned list must be  a list of ele, such as [ele,ele,...ele] or [] which means a leaf-node")
    else:
        print("below is a example:")



#shared_kl = ["nqs","nfa","columns","index","tbl"]
#shared_vl = [[tuple([nfa.q0])],nfa,list(nfa.delta_table.columns),[],[]]

#ele_kl = ["nq"]
#root_vl = [tuple([nfa.q0])]
