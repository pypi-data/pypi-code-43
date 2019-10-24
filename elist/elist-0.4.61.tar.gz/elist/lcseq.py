# https://en.wikipedia.org/wiki/Longest_common_subsequence_problem


# head   l[:-1]
# tail   l[-1]
# car    l[0]
# cdr    l[1:]


from wfsdig import *

####


def split_head_tail(ele,shared,which):
    si = ele["range"+str(which)][0]
    ei = ele["range"+str(which)][1]
    subs = shared["s"+str(which)][si:ei]
    if(len(subs)==0):
        tail = []
        head = []
    else:
        tail = subs[-1]
        head = subs[0:-1]
    return((si,ei,head,tail))

#####

#####
def is_leaf(ele):
    cond0 = (ele["range0"] == (0,0))
    cond1 = (ele["range1"] == (0,0))
    cond = (cond0 | cond1)
    return(cond)

def get_children(ele,shared):
    si0,ei0,head0,tail0 = split_head_tail(ele,shared,0)
    si1,ei1,head1,tail1 = split_head_tail(ele,shared,1)
    if(is_leaf(ele)):
        return([])
    else:
        if(tail0 == tail1):
            #If: xn=ym
            #then: LCS(Xn, Ym) = LCS( Xn-1, Ym-1) ^ xn
            ele["match"] = True
            return([{
                "range0":(si0,ei0-1),
                "range1":(si1,ei1-1),
                "match":None
            }])
        else:
            #LCS(Xn,Ym) = max(LCS(Xn-1, Ym),LCS(Xn, Ym-1))
            left = {
                "range0":(si0,ei0-1),
                "range1":(si1,ei1),
                "match":None
            }
            right = {
                "range0":(si0,ei0),
                "range1":(si1,ei1-1),
                "match":None
            }
            return([left,right])

#####





def encd_leaf_ele(ele,dmat):
    rslt = []
    bpl = ele['_bpl']
    for i in range(len(bpl)-1,-1,-1):
        depth = i
        breadth = bpl[i]
        nd = dmat[depth][breadth]
        if(nd['match'] == True):
            rslt.append(nd)
        else:
            pass
    return(rslt)

def get_all_cmmn(dmat):
    '''
    '''
    rslt = []
    cond_func = lambda ele:(ele['_children'].__len__() == 0)
    depth = len(dmat)
    for i in range(0,depth):
        layer = dmat[i]
        breadth = len(layer)
        for j in range(breadth):
            ele = layer[j]
            cond = cond_func(ele)
            if(cond):
                r = encd_leaf_ele(ele,dmat)
                if(len(r) == 0):
                    pass
                else:
                    rslt.append(r)
            else:
                pass
    return(rslt)



def get_one_cmmn(rslt,shared):
    l = list(map(lambda ele:shared["s0"][ele["range0"][1]-1],rslt))
    return(l)

def get_cmmns(rslts,shared):
    all=[]
    for rslt in rslts:
        all.append(get_one_cmmn(rslt,shared))
    return(all)

def get_one_seq0(rslt):
    l = list(map(lambda ele:ele["range0"][1]-1,rslt))
    return(l)

def get_seqs0(rslts,shared):
    all=[]
    for rslt in rslts:
        all.append(get_one_seq0(rslt))
    return(all)

def get_one_seq1(rslt):
    l = list(map(lambda ele:ele["range1"][1]-1,rslt))
    return(l)

def get_seqs1(rslts,shared):
    all=[]
    for rslt in rslts:
        all.append(get_one_seq1(rslt))
    return(all)


def uniqualize(vs,seqs0,seqs1):
    st = set({})
    for i in range(len(vs)):
        ele = (tuple(vs[i]),tuple(seqs0[i]),tuple(seqs1[i]))
        st.add(ele)
    obj = zip(*list(st))
    return(list(obj))


def lcseq(s0,s1):
    shared = {
        "s0":s0,
        "s1":s1
    } 
    root = {
        "range0":(0,len(shared["s0"])),
        "range1":(0,len(shared["s1"])),
        "match":None
    }
    dig = DIG(shared=shared,root=root,get_children=get_children)
    shared,dmat = dig.final()
    rslts = get_all_cmmn(dmat)
    vs = get_cmmns(rslts,shared)
    seqs0 = get_seqs0(rslts,shared)
    seqs1 = get_seqs1(rslts,shared)
    vs,seqs0,seqs1 = uniqualize(vs,seqs0,seqs1)
    return({
        "values":vs,
        "seqs0":seqs0,
        "seqs1":seqs1
    })
