import efuntool.efuntool as eftl
import dtable.dtable as dtdt
import itertools
import elist.elist as elel
import edict.edict as eded
import math


#1-1 
#1-2
def blnot(p,*args):
    count = args[0] if(len(args)==0) else 1
    cond = not(p) if( (count%2) == 1) else p
    return(cond)

def identity(o0,o1):
    cond0 = (type(o0) == type(o1))
    cond1 = (o0 == o1)
    return((cond0 and cond1))

def is_zero_len(value):
    try:
        rslt = (len(value)==0)
    except:
        return(False)
    else:
        return(rslt)


def is_fls(value,*args):
    if(len(args)==0 or args[0] == []):
        rslt = True if(identity(value,0) or identity(value,False) or (value == None) or is_zero_len(value) ) else False
        return(rslt)
    else:
        flses = args[0]
        for i in range(len(flses)):
            if(identity(value,flses[i])):
                return(True)
            else:
                pass
        return(False)


def bland(*args,**kwargs):
    base = eftl.dflt_kwargs('base',True,**kwargs)
    flses = eftl.dflt_kwargs('flses',[],**kwargs)
    for i in range(len(args)):
        cond = False if(is_fls(args[i],flses)) else True
        base = (base and cond)
    return(base)


def blor(*args,**kwargs):
    base = eftl.dflt_kwargs('base',False,**kwargs)
    flses = eftl.dflt_kwargs('flses',[],**kwargs)
    for i in range(len(args)):
        cond = False if(is_fls(args[i],flses)) else True
        base = (base or cond)
    return(base)


def bland_rtrn_last(*args,**kwargs):
    base = eftl.dflt_kwargs('base',True,**kwargs)
    flses = eftl.dflt_kwargs('flses',[],**kwargs)
    for i in range(len(args)):
        cond = False if(is_fls(args[i],flses)) else True
        if(cond):
            base = args[i]
        else:
            return(False)
    return(base)


def blor_rtrn_first(*args,**kwargs):
    base = eftl.dflt_kwargs('base',False,**kwargs)
    flses = eftl.dflt_kwargs('flses',[],**kwargs)
    for i in range(len(args)):
        cond = False if(is_fls(args[i],flses)) else True
        if(cond):
            base = args[i]
            break
        else:
            pass
    return(base)


def scond(p,q):
    return(not(p) or q)

def dcond(p,q):
    return(scond(p,q) and scond(q,p))

def blxor(p,q):
    return(not(dcond(p,q)))

#1-3
#1-4
#1-5
#ifnt           ifnot


def product(l,repeat=2,**kwargs):
    st = eftl.dflt_kwargs("sort",False,**kwargs) 
    rslt = itertools.product(l,repeat=repeat)
    rslt = list(rslt)
    rslt = elel.mapv(rslt,list,[])
    rslt = elel.mapv(rslt,sorted,[]) if(st) else rslt
    return(rslt)




def permutate(l,repeat=2,**kwargs):
    st = eftl.dflt_kwargs("sort",False,**kwargs)
    rslt = [each for each in itertools.permutations(l,repeat)]
    rslt = list(rslt)
    rslt = elel.mapv(rslt,list,[])
    rslt = elel.mapv(rslt,sorted,[]) if(st) else rslt
    return(rslt)

def permutate_all(l,*args,**kwargs):
    '''
        >>> permutate_all(['a','b','c'])
        [[], ['a'], ['b'], ['c'], ['a', 'b'], ['a', 'c'], ['a', 'b'], ['b', 'c'], ['a', 'c'], ['b', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c']]
        >>>
    '''
    lngth = (len(l)+1) if (len(args)==0) else args[0]
    rslt = []
    for i in range(lngth):
        tmp = permutate(l,repeat=i,**kwargs)
        rslt.extend(tmp)
    return(rslt)



def combinate(l,repeat=2,**kwargs):
    st = eftl.dflt_kwargs("sort",False,**kwargs)
    rslt = [each for each in itertools.combinations(l,repeat)]
    rslt = list(rslt)
    rslt = elel.mapv(rslt,list,[])
    rslt = elel.mapv(rslt,sorted,[]) if(st) else rslt
    return(rslt)

def combinate_all(l,*args,**kwargs):
    '''
        >>> combinate_all(['a','b','c'])
        [[], ['a'], ['b'], ['c'], ['a', 'b'], ['a', 'c'], ['b', 'c'], ['a', 'b', 'c']]
        >>>
    '''
    lngth = (len(l)+1) if (len(args)==0) else args[0]
    rslt = []
    for i in range(lngth):
        tmp = combinate(l,repeat=i,**kwargs)
        rslt.extend(tmp)
    return(rslt)



def creat_tru_fls_mat(cnl,*args):
    rl = eftl.optional_arg([True,False],*args)
    count = len(cnl)
    m = product(rl,count)
    return(m)


def creat_tru_fls_dtb(cnl,*args):
    '''
        >>> cnl
        ['A', 'B', 'C']
        >>>
        >>> parr(creat_tru_fls_dtb(cnl))
        {'A': True, 'B': True, 'C': True, '@RSLT@': None}
        {'A': False, 'B': True, 'C': True, '@RSLT@': None}
        {'A': False, 'B': True, 'C': True, '@RSLT@': None}
        {'A': False, 'B': False, 'C': True, '@RSLT@': None}
        {'A': False, 'B': True, 'C': True, '@RSLT@': None}
        {'A': False, 'B': False, 'C': True, '@RSLT@': None}
        {'A': False, 'B': False, 'C': True, '@RSLT@': None}
        {'A': False, 'B': False, 'C': False, '@RSLT@': None}
        >>>
    '''
    dtb = dtdt.init_dtb(creat_tru_fls_mat(cnl),cnl)
    dtb = dtdt.add_col(dtb,"@RSLT@",elel.init(len(dtb),None))
    return(dtb)

    
# v          or
# ^          and
# ->         if P then Q else true 
# <-         if Q then P else true
# <->
# P=>Q       P->Q always true  求出真值表 然后选取结果 全是true的行
# P<=Q       Q->P always true  
# P<=>Q      


###################################
# 1-6

#if          if  
#ifnt        if-not
#thenfls     then-false
#thentru     then-true
#elfls       else-false
#eltru       else-true

#notp        notp
#notq        notq


def if_p_then_q_else_true(p,q):
    '''
        p->q
        not(p) or q
        或(非p)
        条件
    '''
    return(scond(p,q))

def notp_or_q(p,q):
    return(scond(p,q))

def parrowq(p,q):
    return(scond(p,q))

def if_p_then_q_else_notq(p,q):
    '''
        p<->q
        notporq_and_pornotq
        与(或(非p),或(非q))
        双向条件
    '''
    return(dcond(p,q))

def notporq_and_pornotq(p,q):
    return(dcond(p,q))



####
def if_p_then_notq_else_q(p,q):
    '''
        p^q
        pandnotq_or_notpandq
        异或
        not_dcond
        否定双向条件
    '''
    return(not(dcond(p,q)))

def pandnotq_or_notpandq(p,q):
    return(not(dcond(p,q)))

def not_dcond(p,q):
    return(not(dcond(p,q)))

####

def if_p_then_notq_else_false(p,q):
    '''
        非p-或-非 not(or(not(p),q))
        p_and_notq
        not_scond
        条件否定
    '''
    return(p and not(q))

def p_and_notq(p,q):
    return(p and not(q))

def not_scond(p,q):
    return(not(scond(p,q)))

####################################

def if_p_then_notq_else_true(p,q):
    '''
        与-非 not(and(p,q))
        notp_or_notq
        not_pandq
    '''
    return(not(p) or not(q))

def notp_or_notq(p,q):
    return(not(p) or not(q))

def not_pandq(p,q):
    return(not(p and q))

#####################################

def if_p_then_false_else_notq(p,q):
    '''
        或-非 not(or(p,q))
        notp_and_notq
    '''
    return(not(p) and not(q))

def notp_and_notq(p,q):
    return(not(p) and not(q))

def not_porq(p,q):
    return(not(p or q))


#######################################

def _get_permutation_map(arr,**kwargs):
    arr = sorted(arr,**kwargs)
    mp = elel.ivdict(arr)
    return(mp)

def _recover_via_permutation_map(kl,mp):
    vl = eded.vlviakl(mp,kl)
    return(vl)

def binlist2permutation(binlist,arr,**kwargs):
    mp = _get_permutation_map(arr,**kwargs)
    vl = _recover_via_permutation_map(kl,mp)
    return(vl)

def permutation2binlist(permu,**kwargs):
    mp = _get_permutation_map(permu,**kwargs)
    kl = eded.klviavl(mp,permu)
    return(kl)

def _next_permutation(arr):
    pair = elel.find_fst_indexpair_fstltsnd_via_reversing(arr)
    if(pair == None):
        return(None)
    else:
        j = elel.find_fst_index_gt_via_reversing(arr[pair[0]],arr)
        arr = elel.swap(pair[0],j,arr)
        init  = arr[:pair[1]]
        tail  = sorted(arr[pair[1]:])
        arr = elel.concat(init,tail)
        return(arr)

def next_permutation(vl,**kwargs):
    mp = _get_permutation_map(vl,**kwargs)
    kl = eded.klviavl(mp,vl)
    kl = _next_permutation(kl)
    if(kl == None):
        return(None)
    else:
        pass
    vl = _recover_via_permutation_map(kl,mp)
    return(vl)


def _prev_permutation(arr):
    pair = elel.find_fst_indexpair_fstgtsnd_via_reversing(arr)
    if(pair == None):
        return(None)
    else:
        j = elel.find_fst_index_lt_via_reversing(arr[pair[0]],arr)
        arr = elel.swap(pair[0],j,arr)
        init  = arr[:pair[1]]
        tail  = sorted(arr[pair[1]:])
        tail.reverse()
        arr = elel.concat(init,tail)
        return(arr)

def prev_permutation(vl,**kwargs):
    mp = _get_permutation_map(vl,**kwargs)
    kl = eded.klviavl(mp,vl)
    kl = _prev_permutation(kl)
    if(kl == None):
        return(None)
    else:
        pass
    vl = _recover_via_permutation_map(kl,mp)
    return(vl)


def _get_permutation_index(arr):
    indexes = []
    lngth = len(arr)
    for i in range(lngth):
        lefted = arr[i:lngth]
        lefted = sorted(lefted)
        indexes.append(lefted.index(arr[i]))
    indexes = elel.filter(indexes,lambda index:index>0)
    acc = 0
    for i in range(len(indexes)):
        acc = acc + indexes[i] * math.factorial(lngth-i-1)
    return(acc)

def permutation2index(vl,**kwargs):
    '''
        >>> permutation2index(['c','d','b','a','e'])
        62
        >>>
    '''
    mp = _get_permutation_map(vl,**kwargs)
    kl = eded.klviavl(mp,vl)
    index = _get_permutation_index(kl)
    return(index)

def _relindex2absindex(indexes):
    '''
        >>> _relindex2absindex([2,2,1,1,0])
        [2, 3, 1, 4, 0]
        >>>
        [2, 3, 1, 4, 0]                               [2,2,1,1,0]
        2                           arr=[0,1,2,3,4]   2=arr[2]
                                    arr.pop(2)
        3                           arr=[0,1,3,4]     3=arr[2]
                                    arr.pop(2)
        1                           arr=[0,1,4]       1=arr[1]
                                    arr.pop(1)
        4                           arr=[0,4]         4=arr[1]
                                    arr.pop(1)
        0                           arr=[0]           0=arr[0]
    '''
    lngth = len(indexes)
    arr = elel.init_range(0,lngth,1)
    rslt = []
    for i in range(lngth):
        ri = indexes[i]
        index = arr[ri]
        ai = arr.pop(ri)
        rslt.append(ai)
    return(rslt)


def index2permutation(index,lngth,*args):
    '''
        >>> index2permutation(62,5)
        [2, 3, 1, 0, 4]
        >>>
        >>> index2permutation(62,5,['a','b','c','d','e'])
        ['c', 'd', 'b', 'a', 'e']
        >>>
    '''
    rel_indexes = []
    n = lngth - 1
    while(index>0):
        q = index // math.factorial(n)
        r = index % math.factorial(n)
        rel_indexes.append(q)
        n = n - 1
        index = r
    if(len(args)==0):
        arr = elel.init_range(0,lngth,1)
    else:
        arr = args[0]
    rel_indexes = elel.padding(rel_indexes,lngth,0)
    abs_indexes = _relindex2absindex(rel_indexes)
    rslt = elel.select_seqs(arr,abs_indexes)
    return(rslt)   
        


class Permutation():
    '''
        >>> p=Permutation(['a','b','c','d'])
        >>> p
        ['a', 'b', 'c', 'd']
        >>> p.next()
        ['a', 'b', 'd', 'c']
        >>> p.next()
        ['a', 'c', 'b', 'd']
        >>> p.prev()
        ['a', 'b', 'd', 'c']
        >>> p.prev()
        ['a', 'b', 'c', 'd']
    '''
    def __init__(self,vl,*args,**kwargs):
        if(isinstance(vl,list)):
            self.seed = vl
            self.curr = vl
        else:
            index = vl
            self.seed = index2permutation(index,lngth,*args)
            self.curr = self.seed
        self.kwargs = kwargs
    def next(self):
        self.curr = next_permutation(self.curr,**self.kwargs)
        #print(self.curr.__str__())
        return(elel.fcp(self.curr))
    def prev(self):
        self.curr = prev_permutation(self.curr,**self.kwargs)
        #print(self.curr.__str__())
        return(elel.fcp(self.curr))
    def index(self):
        i = permutation2index(self.curr,**self.kwargs)
        return(i)
    def __repr__(self):
        return(self.curr.__str__())

####
####
def _get_combination_map(arr,**kwargs):
    '''
        >>> _get_combination_map(['a','b','c','d','e'])
        {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'}
        >>>
    '''
    arr = sorted(arr,**kwargs)
    mp = elel.ivdict(arr)
    return(mp)


def _get_combination_num(combi,arr):
    '''
        >>> _get_combination_num(["c","e"],["a","b","c","d","e"])
        20     1 0 1 0 0
               e d c b a
        >>>
    '''
    mp = _get_combination_map(arr)
    combi = elel.mapv(combi,lambda ele:arr.index(ele))
    num = elel.reduce_left(combi,lambda acc,ele:acc+2**ele,0)
    return(num)


def binlist2num(binlist,**kwargs):
    bigend = eftl.dflt_kwargs('bigend',True,**kwargs)
    if(bigend):
        pass
    else:
        binlist = elel.fcp(binlist)
        binlist.reverse()
    arr = elel.mapv(binlist,str)
    s = elel.join(arr)
    return(int(s,2))


def num2binlist(num,**kwargs):
    '''
        >>> num2binlist(2)
        [1, 0]
        >>> num2binlist(3)
        [1, 1]
        >>> num2binlist(3,size=4)
        [0, 0, 1, 1]
        >>>
    '''
    bitmap_size = eftl.dflt_kwargs('size',bin(num).__len__() - 2,**kwargs)
    bigend = eftl.dflt_kwargs('bigend',True,**kwargs)
    bitmaplist = []
    s = bin(num)[2:]
    s_len = s.__len__()
    for i in range(0,s_len):
        b = s[s_len-i-1]
        bitmaplist.append(int(b))
    for i in range(s_len,bitmap_size):
        bitmaplist.append(0)
    if(bigend):
        bitmaplist.reverse()
    else:
        pass
    return(bitmaplist)

def combination2binlist(combi,arr):
    '''
        >>> combination2binlist(["c","e"],['a', 'b', 'c', 'd', 'e'])
        [1, 0, 1, 0, 0]
        >>>
    '''
    n = _get_combination_num(combi,arr)
    lngth = len(arr)
    binlist = num2binlist(n,bigend=True,size=lngth)
    return(binlist)

def _get_minbinlist(tl):
    '''
        >>> _get_minbinlist([1,0,1])
        [0, 1, 1]
        >>>
    '''
    tl_len = len(tl)
    if(tl_len == 0):
        return(tl)
    else:
        pass
    cnt = tl.count(1)
    tl = num2binlist(2**cnt-1,size=tl_len)
    return(tl)

def _get_maxbinlist(tl):
    '''
        >>> _get_maxbinlist([1,0,1])
        [1,1,0]
        >>>
    '''
    tl = _get_minbinlist(tl)
    tl.reverse()
    return(tl)


def _next_combination(binlist):
    '''
        >>> binlist = [1, 0, 0, 1, 1]
        >>>
        >>> _next_combination(binlist)
        [1, 0, 1, 0, 1]
        >>>
        >>> _next_combination(binlist)
        [1, 0, 1, 1, 0]
        >>> _next_combination(binlist)
        [1, 1, 0, 1, 0]
        >>> _next_combination(binlist)
        [1, 1, 1, 0, 0]
        >>> _next_combination(binlist)
        >>>
        >>> binlist = [1, 0, 1, 1, 0]
        >>> _next_combination(binlist)
        [1, 1, 0, 1, 0]
        >>> _next_combination(binlist)
        [1, 1, 1, 0, 0]
        >>> _next_combination(binlist)
        >>>
    '''
    lngth = len(binlist)
    last = binlist[-1]
    if(last == 1):
        last_zero_index = elel.find_fst_index_eq_via_reversing(0,binlist)
        if(last_zero_index == None):
            return(None)
        else:
            pass
        next_one_index = last_zero_index + 1
        elel.swap(last_zero_index,next_one_index,binlist)
        #
        hl = binlist[:next_one_index+1]
        tl = binlist[next_one_index+1:]
        tl = _get_minbinlist(tl)
        binlist = elel.concat(hl,tl)
        #
    else:
        last_one_index = elel.find_fst_index_eq_via_reversing(1,binlist)
        prev_zero_index = elel.find_fst_index_eq_via_reversing(0,binlist[:last_one_index])
        if(prev_zero_index == None):
            return(None)
        else:
            pass
        prev_one_index = prev_zero_index + 1
        elel.swap(prev_zero_index,prev_one_index,binlist)
        #
        hl = binlist[:prev_one_index+1]
        tl = binlist[prev_one_index+1:]
        tl = _get_minbinlist(tl)
        binlist = elel.concat(hl,tl)
        #
    return(binlist)


def _binlist2combination(binlist,arr):
    '''
        >>> _binlist2combination([1,0,1,0,0],["a","b","c","d","e"])
        ['c', 'e']
        >>>
    '''
    mp = _get_combination_map(arr)
    rslt = []
    lngth = len(binlist)
    for i in range(lngth):
        if(binlist[i] == 1):
            rslt.append(arr[lngth-1-i])
        else:
            pass
    rslt.sort()
    return(rslt)

def binlist2combination(binlist,arr):
    return(_binlist2combination(binlist,arr))

def _get_next_level_fst_binlist(combi,lngth):
    '''
        >>> _get_next_level_fst_binlist(["x"],5)
        [0, 0, 0, 1, 1]
        >>> _get_next_level_fst_binlist(["x","x"],5)
        [0, 0, 1, 1, 1]
        >>> _get_next_level_fst_binlist([],5)
        [0, 0, 0, 0, 1]
        >>> _get_next_level_fst_binlist(["x","x","x","x","x"],5)
        >>>
    '''
    curr_len = len(combi)
    if(curr_len == lngth):
        return(None)
    else:
        n = 2**(curr_len + 1) - 1
        binlist = num2binlist(n,size=lngth)
        return(binlist)

def _get_prev_level_lst_binlist(combi,lngth):
    '''
        >>> _get_prev_level_lst_binlist([],5)
        >>> _get_prev_level_lst_binlist(["x"],5)
        [0, 0, 0, 0, 0]
        >>> _get_prev_level_lst_binlist(["x","x"],5)
        [1, 0, 0, 0, 0]
        >>>
    '''
    curr_len = len(combi)
    if(curr_len == 0):
        return(None)
    else:
        n = 2**curr_len  - 2
        binlist = num2binlist(n,size=lngth)
        binlist = _get_maxbinlist(binlist)
        return(binlist)

def next_combination(combi,arr):
    '''
        >>> next_combination(["c","e"],["a","b","c","d","e"])
        ['d', 'e']
        >>> next_combination(["d","e"],["a","b","c","d","e"])
        ['a', 'b', 'c']
        >>> next_combination(["a","b","c"],["a","b","c","d","e"])
        ['a', 'b', 'd']
        >>>
        >>> next_combination(["a","b","c","d"],["a","b","c","d","e"])
        ['a', 'b', 'c', 'e']
        >>> next_combination(["a","b","c","d","e"],["a","b","c","d","e"])
        >>>
    '''
    if(len(combi) == 0):
         mp = _get_combination_map(arr)
         return([mp[0]])
    else:
        pass
    lngth = len(arr)
    binlist = combination2binlist(combi,arr)
    binlist = _next_combination(binlist)
    if(binlist == None):
        binlist = _get_next_level_fst_binlist(combi,lngth)
        if(binlist == None):
            return(None)
        else:
            pass
    else:
        pass
    rslt = _binlist2combination(binlist,arr)
    return(rslt)



def _prev_combination(binlist):
    '''
        >>> _prev_combination([1,1,1,1,1])
        >>> _prev_combination([1,1,1,0,1])
        [1, 1, 0, 1, 1]
        >>> _prev_combination([1,1,0,1,1])
        [1, 0, 1, 1, 1]
        >>>
        >>> _prev_combination([1,0,1,1,1])
        [0, 1, 1, 1, 1]
        >>> _prev_combination([0,1,1,1,1])
        >>>
        >>>
        >>> _prev_combination([1, 0, 1, 1, 0])
        [1, 0, 1, 0, 1]
        >>>
        >>> _prev_combination([1, 0, 1,0,1])
        [1, 0, 0, 1, 1]
        >>>
        >>> _prev_combination([1, 0, 0,1,1])
        [0, 1, 0, 1, 1]
        >>> _prev_combination([0,1,0,1,1])
        [0, 0, 1, 1, 1]
        >>> _prev_combination([0,0,1,1,1])
        >>>
    '''
    lngth = len(binlist)
    last = binlist[-1]
    if(last == 1):
        '''
            [1,0,0,1,1]
               ^-------------------find this 0
            [0,1,0,1,1]
             ^ ^ ------------------swap with 1 after this 0
            [1,0,1,0,1]
                   ^-------------------find this 0
            [0,1,1,0,1]
                 ^ ^ ------------------swap with 1 after this 0             
            [1,1,1,1,1]  --------None
            [0,0,1,1,1]  --------None     0...0  1...1  
        '''
        #从后往前找,find last zero
        last_zero_index = elel.find_fst_index_eq_via_reversing(0,binlist)
        if(last_zero_index == None):
            return(None)
        else:
            pass
        #从last-zero开始,从后往前找, 找到第一个1
        prev_one_index = elel.find_fst_index_eq_via_reversing(1,binlist[:last_zero_index])
        if(prev_one_index == None):
            return(None)
        else:
            pass
        #这个1后面(从前往后)肯定是0，记录这个0
        prev_zero_index = prev_one_index +1
        elel.swap(prev_zero_index,prev_one_index,binlist)
        #
        hl = binlist[:prev_zero_index+1]
        tl = binlist[prev_zero_index+1:]
        tl = _get_maxbinlist(tl)
        binlist = elel.concat(hl,tl)
        #
    else:
        '''
            [1,0,1,1,0]
                   ^----------------------find this 1
            [1,0,1,1,0]
                   ^ ^ --------------------swap with 1 before this 0
            [0,0,0,0,0]-----------------None
        '''
        last_one_index = elel.find_fst_index_eq_via_reversing(1,binlist)
        if(last_one_index == None):
            return(None)
        else:
            pass
        next_zero_index = last_one_index + 1
        elel.swap(next_zero_index,last_one_index,binlist)
        #
        hl = binlist[:next_zero_index+1]
        tl = binlist[next_zero_index+1:]
        tl = _get_maxbinlist(tl)
        binlist = elel.concat(hl,tl)
        #
    return(binlist)

def prev_combination(combi,arr):
    '''
        >>> prev_combination(["a","c"],["a","b","c","d","e"])
        ['a', 'b']
        >>> prev_combination(["a","b"],["a","b","c","d","e"])
        ['a']
        >>> prev_combination(["a"],["a","b","c","d","e"])
        []
        >>> prev_combination([],["a","b","c","d","e"])
        >>>
        >>> prev_combination(["a","b","c","d"],["a","b","c","d","e"])
        ['a', 'b', 'c']
        >>> prev_combination(["a","b","c","e"],["a","b","c","d","e"])
        ['a', 'b', 'c', 'd']
        >>>
        >>> prev_combination(["a","b","c","d","e"],["a","b","c","d","e"])
        ['b', 'c', 'd', 'e']
        >>>
    '''
    lngth = len(arr)
    binlist = combination2binlist(combi,arr)
    binlist = _prev_combination(binlist)
    if(binlist == None):
        binlist = _get_prev_level_lst_binlist(combi,lngth)
        if(binlist == None):
            return(None)
        else:
            pass
    else:
        pass
    rslt = _binlist2combination(binlist,arr)
    return(rslt)

def get_combination_count(k,n):
    nf = math.factorial(n)
    kf = math.factorial(k)
    nsubkf = math.factorial(n-k)
    rslt = nf // kf
    rslt = rslt // nsubkf
    return(rslt)

def _get_combination_brkpoints(n):
    sizes = [get_combination_count(k,n) for k in range(n+1)]
    brks = elel.interval_sizes2brks(sizes)
    return(brks)

def get_combination_interval(n):
    '''
        >>> get_combination_interval(4)
        [(0, 1), (1, 5), (5, 11), (11, 15), (15, 16)]
        >>>
    '''
    brks = _get_combination_brkpoints(n)
    rngzs = elel.rangize(brks,2**n)
    return(rngzs)

def _combination2index(binlist):
    next = _get_minbinlist(binlist)
    c = 0
    while(next!=binlist):
        next = _next_combination(next)
        c = c + 1
    return(c)

def combination2index(combi,arr):
    '''
        >>> arr
        ['a', 'b', 'c', 'd', 'e']
        >>>
        >>> combination2index([],arr)
        0
        >>> combination2index(['a'],arr)
        1
        >>> combination2index(['b'],arr)
        2
        >>> combination2index(['c'],arr)
        3
        >>>
        >>> combination2index(['a','c'],arr)
        7
        >>> combination2index(arr,arr)
        31
        >>> combination2index(['b','c','d','e'],arr)
        30
        >>>
    '''
    lngth = len(arr)
    intervals = get_combination_interval(lngth)
    combi_len = len(combi)
    interval = intervals[combi_len]
    binlist = combination2binlist(combi,arr)
    rel_index = _combination2index(binlist)
    index = interval[0] + rel_index
    return(index)

def index2combination(index,arr):
    if(index ==0):
        return([])
    else:
        lngth = len(arr)
        intervals = get_combination_interval(lngth)
        which = elel.which_interval_index(index,intervals)
        binlist = num2binlist(2**which-1,size=lngth)
        base = intervals[which][0]
        offset = index - base
        for i in range(offset):
            binlist = _next_combination(binlist)
        combi = binlist2combination(binlist,arr)
        return(combi)

class Combination():
    '''
        >>> c = Combination(['a','b'],['a', 'b', 'c', 'd', 'e'])
        >>>
        >>> c
        ['a', 'b']
        >>>
        >>> c.next()
        ['a', 'c']
        >>> c
        ['a', 'c']
        >>> c.prev()
        ['a', 'b']
        >>> c
        ['a', 'b']
        >>> c.index()
        6
        >>> c = Combination(6,['a', 'b', 'c', 'd', 'e'])
        >>> c
        ['a', 'b']
        >>>
    '''
    def __init__(self,vl,arr,**kwargs):
        self.full = arr 
        if(isinstance(vl,list)):
            self.seed = vl
            self.curr = vl
        else:
            index = vl
            self.seed = index2combination(index,arr)
            self.curr = self.seed
        self.kwargs = kwargs
    def next(self):
        self.curr = next_combination(self.curr,self.full,**self.kwargs)
        return(elel.fcp(self.curr))
    def prev(self):
        self.curr = prev_combination(self.curr,self.full,**self.kwargs)
        return(elel.fcp(self.curr))
    def index(self):
        i = combination2index(self.curr,self.full,**self.kwargs)
        return(i)
    def __repr__(self):
        return(self.curr.__str__())
