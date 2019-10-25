import copy
import elist.elist as elel
from estring.estring import is_int_str,is_float_str
import efuntool.efuntool as eftl

import eobj.kastr as kastr


#pl      pathlist
#ppl     parent-pathlist
#fpl     full-pathlist
#pfpl    

############################

def ppl2pl(tag,ppl):
    pl = elel.fcp(ppl)
    pl.append(tag)
    return(pl)

def pfpl2fpl(ftag,pfpl):
    return(ppl2pl(ftag,pfpl))


def pl2tag(pl):
    return(pl[-1])

def fpl2ftag(fpl):
    return(pl2tag(fpl))


def fpl2depth(fpl):
    '''
        only fpl can get depth
    '''
    return(len(fpl))

##############################

def fpl2pl(fpl):
    '''
        选取非数字的key
    '''
    pl = elel.cond_select_values_all(fpl,eftl.not_wrapper(is_int_str))
    return(pl)

#####################
#apl      attr-pathlist
#fapl     full-attr-pathlist


def fpl2fapl(fpl,typel):
    '''
        >>> wfsm[3][0].typel
        ['dict', 'list', 'dict', 'str']
        >>>
        >>> wfsm[3][0].fpl
        ['body', 0, 'type']
        >>>
        >>> plfuncs.fpl2fapl(['body', 0, 'type'],['dict', 'list', 'dict', 'str'])
        ['body', 'l0_', 'type']
    '''
    fapl = elel.mapiv(fpl,lambda i,k,o:kastr.ftag2fatag(k,o[i]),[typel])
    return(fapl)


def fapl2fpl(fapl):
    '''
        >>> plfuncs.fapl2fpl(['body', 'l0_', 'type'])
        ['body', 0, 'type']
        >>>
    '''
    fpl = elel.mapv(fapl,kastr.fatag2ftag)
    return(fpl)

#########

def _plcmp(pl0,pl1):
    if(pl0 > pl1):
        return(1)
    elif(pl0 == pl1):
        return(0)
    else:
        return(-1)


def plcmp(pl0,pl1,**kwargs):
    '''
        plcmp([0,1,2],[0,1])
        #> 1
        plcmp([1],[0,1])
        #> 1
        plcmp([0,0],[0,1])
        #> -1
    '''
    lngth0 = len(pl0)
    lngth1 = len(pl1)
    break_tie_longer_bigger = eftl.dflt_kwargs("break_tie_longer_bigger",True,**kwargs)
    break_tie = 1 if(break_tie_longer_bigger) else -1
    if(lngth0 == lngth1):
        rslt = _plcmp(pl0,pl1)
    elif(lngth0 > lngth1):
        rslt = _plcmp(pl0[:lngth1],pl1)
        rslt = break_tie if(rslt == 0) else rslt
    else:
        rslt = _plcmp(pl0,pl1[:lngth0])
        rslt = (-break_tie) if(rslt == 0) else rslt
    return(rslt)

####
#ancespl     ancestor-pathlist(s)

def _pl2ancespls(pl):
    '''
        #
        import copy
        from cProfile import run
        
        #
        arr = [0,1,2,3,4]
        lngth = len(arr)
        def wrap(f,*args):
            c = 0
            while(c<100000):
                f(*args)
                c = c+1
        
        #
        def dcp(arr):
            rslt = copy.deepcopy(arr)
            return(rslt)
        
        #
        def cp(arr):
            rslt = copy.copy(arr)
            return(rslt)
        
        #
        def slc0(arr):
            rslt = arr[:]
            return(rslt)
        
        #
        def slc1(arr):
            rslt = arr[0:]
            return(rslt)
        
        #
        def slc2(arr,lngth):
            rslt = arr[:lngth]
            return(rslt)
        
        >>> run("wrap(dcp,arr)")
         4000004 function calls (3500004 primitive calls) in 2.102 seconds
        
        >>> run("wrap(cp,arr)")
                 300004 function calls in 0.175 seconds
        >>> run("wrap(slc0,arr)")
                 100004 function calls in 0.060 seconds
        >>> run("wrap(slc1,arr)")
                 100004 function calls in 0.062 seconds
        
        >>> run("wrap(slc2,arr,lngth)")
                 100004 function calls in 0.069 seconds
        
        #使用这个技巧可以避免copy
        >>> arr
        [0, 1, 2, 3, 4]
        >>>
        >>> arr1 = arr[:] #
        >>>
        >>> id(arr)
        140172432609992 #--------------->
        >>>
        >>> id(arr1)
        140172432611592 #--------------->
        >>>
        >>> pl
        ['a', 'bb', 1, 'c']
        >>>
        >>> id(pl)
        140172432610440
        >>>
        >>> id(pl[:1])     #------这里是inplace的,没有发生复制
        140172432610760
        >>>
        >>> id(pl[:2])     #------这里是inplace的,没有发生复制
        140172432610760
        >>>
        >>> tmp = [pl[:1],pl[:2]]    #---------->这个动作隐含复制pl[:2],因为[...]初始化数组其实是赋值给匿名变量
        >>> id(tmp[0])
        140172432610760
        >>> id(tmp[1])
        140172432611656              #---------->复制pl[:2]后
        >>>
        >>> tmp[0].append("append-to-tmp[0]")
        >>> tmp
        [['a', 'append-to-tmp[0]'], ['a', 'bb']]
        >>>
        >>> pl
        ['a', 'bb', 1, 'c']
        >>>
        再看下面
        >>> pl
        ['a', 'bb', 1, 'c']
        >>>
        >>>
        >>> id(pl)
        140172432610440
        >>> id(pl[:1])
        140172432611464
        >>> id(pl[:2])
        140172432611464    #=============================》注意比较
        >>>
        >>> pl1 = pl[:1]
        >>> pl2 = pl[:2]   #----------------------->显式赋值，会触发部分数组slice隐含复制动作
        >>> id(pl1)
        140172432611464
        >>> id(pl2)
        140172432604808 #=============================》内存变啦
        >>>
    '''
    pls = elel.mapi(pl,lambda i,o:o[:i],[pl])
    pls.append(pl[:])
    pls.reverse()
    return(pls)

def pl2ancespl(pl,*args):
    '''
        >>> pl
        [0, 1, 2, 3, 4]
        >>>
        >>> pl2ancespl(pl)
        [[0, 1, 2, 3], [0, 1, 2], [0, 1], [0], []]
        >>>
        >>> pl2ancespl(pl,0)
        [0, 1, 2, 3,4]
        >>> pl2ancespl(pl,1)
        [0, 1, 2]
        >>> pl2ancespl(pl,2)
        [0, 1]
        >>> pl2ancespl(pl,3)
        [0]
        >>> pl2ancespl(pl,4)
        []
    '''
    ancespls = _pl2ancespls(pl)
    pls = eftl.optional_whiches(ancespls,'all',*args)
    return(pls)
            


##gistr  -----  getitem-string
##>>> elel.pl2gs([1,2,'1'])
##"[1][2]['1']"


