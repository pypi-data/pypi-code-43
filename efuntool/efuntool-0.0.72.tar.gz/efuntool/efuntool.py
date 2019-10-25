import functools
import copy
import elist.elist as elel
import inspect


######################################################
# lambda number
# this will count how many recursives done 
###########

def cygnus():
    def egg(*o):
        lngth = len(o)
        if(lngth == 0):
            egg.count = 1
            return(egg)
        else:
            o = o[0]
            o.count = o.count + 1
        return(o)
    egg.__setattr__("count",0)
    return(egg)

#####################################
# how many calls done
#####################################

def duck():
    def egg():
        egg.count = egg.count + 1
        return(egg)
    egg.__setattr__("count",0)
    return(egg)


#########
#params history record
##############

def hen():
    def egg(zero):
        if(hasattr(egg,zero)):
            count = egg.__getattribute__(zero)
            count = count + 1
            egg.__setattr__(zero,count)
        else:
            egg.__setattr__(zero,1)
        return(egg)
    return(egg)


########################################################
##simulate  curry

def goose():
    def egg(*args):
        egg.arguments.extend(args)
        return(egg)
    egg.__setattr__("arguments",[])
    return(egg)


class curry():
    def __init__(self,orig_func,params_count):
        self.orig_func = orig_func
        self.params_count = params_count
        self.egg = goose()
    def __call__(self,*args):
        count = self.params_count
        orig_func = self.orig_func
        egg = self.egg
        egg(*args)
        args_lngth = len(egg.arguments)
        if(args_lngth<count):
            return(self)
        else:
            args = egg.arguments
            egg.arguments = []
            return(orig_func(*args))

########################################################

def reorder_params_trans(f,param_seqs):
    def new_func(*args):
        new_sorted_args = elel.select_seqs(args,param_seqs)
        return(f(*new_sorted_args))
    return(new_func)

def args2dict_trans(f):
    arg_names = inspect.getfullargspec(f).args
    def _func(arg_names,d):
        args = []
        for i in range(len(arg_names)):
            k = arg_names[i]
            args.append(d[k])
        return(f(*args))
    func = functools.partial(_func,arg_names)
    return(func)

##############################################

def deepcopy_wrapper(func):
    '''
        inplace or not
        dflt not
    '''
    @functools.wraps(func)
    def wrapper(obj,*args,**kwargs):
        inplace = dflt_kwargs('inplace',False,**kwargs)
        if(inplace):
            return(func(obj,*args,**kwargs))
        else:
            nobj = copy.deepcopy(obj)
            return(func(nobj,*args,**kwargs))
    return(wrapper)


def force_deepcopy_wrapper(func):
    @functools.wraps(func)
    def wrapper(obj,*args,**kwargs):
        nobj = copy.deepcopy(obj)
        return(func(nobj,*args,**kwargs))
    return(wrapper)

#######################################################

def force_deepcopy_and_keep_ptr_wrapper(func):
    @functools.wraps(func)
    def wrapper(obj,*args,**kwargs):
        nobj = copy.deepcopy(obj)
        nobj = func(nobj,*args,**kwargs)
        obj.clear()
        if(isinstance(obj,list)):
            obj.extend(nobj)
        elif(isinstance(obj,dict)):
            obj.update(nobj)
        else:
            pass
        return(obj)
    return(wrapper)

def force_inplace_and_keep_ptr_wrapper(func):
    @functools.wraps(func)
    def wrapper(obj,*args,**kwargs):
        nobj = func(obj,*args,**kwargs)
        obj.clear()
        if(isinstance(obj,list)):
            obj.extend(nobj)
        elif(isinstance(obj,dict)):
            obj.update(nobj)
        else:
            pass
        return(obj)
    return(wrapper)


def deepcopy_and_keep_ptr_wrapper(func):
    @functools.wraps(func)
    def wrapper(obj,*args,**kwargs):
        keep_ptr = dflt_kwargs('keep_ptr',False,**kwargs)
        deep_copy =  dflt_kwargs('deep_copy',True,**kwargs)
        nobj = (copy.deepcopy(obj) if(deep_copy) else obj)
        nobj = func(nobj,*args,**kwargs)
        if(keep_ptr):
            obj.clear()
            if(isinstance(obj,list)):
                obj.extend(nobj)
            elif(isinstance(obj,dict)):
                obj.update(nobj)
            else:
                pass
            return(obj)
        else:
            return(nobj)
    return(wrapper)


################

def dflt_sysargv(dflt,which):
    import sys as currsys
    try:
        rslt = currsys.argv[which]
    except:
        rslt = dflt
    else:
        pass
    return(rslt)


def dflt_kwargs(k,dflt,**kwargs):
    '''
       counts = dflt_kwargs("counts",100,**kwargs)
    '''
    if(k in kwargs):
        v = kwargs[k]
    else:
        v = dflt
    return(v)




def self_kwargs(self,kl,dfltl,**kwargs):
    '''
        in class  __init__
        kwargs  to  property
        kwargs_to_property_in_cls_init
    '''
    for i in range(len(kl)):
        k = kl[i]
        if(k in kwargs):
            self.__setattr__(k,kwargs[k])
        else:
            self.__setattr__(k,dfltl[i])
    return(self)

def kwargs_to_property_in_cls_init(self,kl,dfltl,**kwargs):
    '''
        >>> class tst():
        ...     def __init__(self,**kwargs):
        ...         eftl.self_kwargs(self,['name','age'],['stu','20'],**kwargs)
        ...
        >>> p = tst()
        >>> p.name
        'stu'
        >>> p.age
        '20'
        >>> p = tst(name='terry')
        >>> p.name
        'terry'
        >>> p.age
        '20'
        >>>
    '''
    return(self_kwargs(self,kl,dfltl,**kwargs))


def de_args(kl,dfltl,*args):
    '''
        dictize args
        de_args(kl,dfltl,*args)

        kl = ['k1','k2','k3','k4']
        dfltl = [3,4]
        de_args(kl,dfltl,'a','b')
        {
            'k1':'a',
            'k2':'b',
            'k3':3,
            'k4':4
        }
    '''
    d = {}
    args_len = len(args)
    kl_len = len(kl)
    for i in range(args_len):
        k = kl[i]
        d[k] = args[i]
    for i in range(args_len,kl_len):
        k = kl[i]
        d[k] = dfltl[i]
    return(d)


def dictize_args(kl,dfltl,*args):
    '''
        dictize args
        dictize_args(kl,dfltl,*args)

        kl = ['k1','k2','k3','k4']
        dfltl = [3,4]
        dictize_args(kl,dfltl,'a','b')
        {
            'k1':'a',
            'k2':'b',
            'k3':3,
            'k4':4
        }
    '''
    return(de_args(kl,dfltl,*args))


def compatibize_apply_or_call_args(*args,**kwargs):
    '''
        >>> eftl.compatibize_apply_or_call_args(1,2,3)
        [1, 2, 3]
        >>>
        >>> eftl.compatibize_apply_or_call_args([1,2,3])
        [1, 2, 3]
        >>>
        >>> eftl.compatibize_apply_or_call_args([1])
        [1]
        >>> eftl.compatibize_apply_or_call_args(1)
        [1]
        >>>
    '''
    args = list(args)
    lngth  = len(args)
    if(lngth == 0):
        pass
    elif(lngth >= 2):
        pass
    else:
        if(isinstance(args[0],list)):
            args  = args[0]
        else:
            pass
    return(args)


def optional_arg(dflt,*args):
    '''
        arg = optional_arg(100)
        arg
        >>>100
        arg = optional_arg(100,250)
        arg
        >>>250
    '''
    arg = dflt if(len(args)==0) else args[0]
    return(arg)

def optional_which_arg(dflt,*args):
    which = dflt if(len(args)==0) else args[0]
    return(which)


def optional_whiches(arr,dflt,*args):
    '''
        #optional_whiches(arr,dflt,*args)
        >>> optional_whiches([10,11,12,13],1)
        11
        >>> optional_whiches([10,11,12,13],'all')
        [10, 11, 12, 13]
        >>>
        >>> optional_whiches([10,11,12,13],'all',1,3)
        [11, 13]
        >>>
        >>> optional_whiches([10,11,12,13],'all',2)
        12
        >>>
        >>> optional_whiches([10,11,12,13],'all','last')
        13
        >>> optional_whiches([10,11,12,13],'all','first')
        10
        >>>
    '''
    lngth = len(args)
    if(lngth >= 2):
        whiches = args
        return(elel.select_seqs(arr,whiches))
    else:
        which = optional_which_arg(dflt,*args)
        if(which == 'all'):
            return(arr)
        elif(which == 'last'):
            return(arr[-1])
        elif(which == 'first'):
            return(arr[0])
        else:
            return(arr[which])


#################################

def pipeline(funcs):
    def _pipeline(funcs,arg):
        func = funcs[0]
        arg = func(arg)
        for i in range(1,len(funcs)):
            func = funcs[i]
            arg = func(arg)
        return(arg)
    p = functools.partial(_pipeline,funcs)
    return(p)


def params_pipeline(f,orig,*args):
    for i in range(len(args)):
        orig = f(orig,*args[i])
    return(orig)

####


def ternaryop(cond,if_tru_rslt,if_fls_rslt):
    '''
        >>> ternaryop(3>2,"ye!","no")
        'ye!'
        >>> ternaryop(3<2,"ye!","no")
        'no'
        >>>
    '''
    rslt = if_tru_rslt if(cond) else if_fls_rslt
    return(rslt)


def ifchain(paramd,*args):
    '''
        f0 = lambda ele:"condition 0"
        f1 = lambda ele:"condition 1"
        final = lambda ele:"else"
        cond0 = 3<2
        cond1 = 3>2
        ifchain({},cond0,f0,cond1,f1,final)
        'condition 1'
        >>>
    '''
    kl = elel.select_evens(args)
    vl = elel.select_odds(args)
    rslt = None
    for i in range(len(kl)):
        cond = kl[i]
        if(cond):
            return(vl[i](paramd))
        else:
            pass
    return(vl[-1](paramd))


def bool_op(op,cond1,cond2):
    op = op.lower()
    if(op == "and"):
        return(bool(cond1 and cond2))
    elif(op == "or"):
        return(bool(cond1 or cond2))
    elif(op == "not"):
        return(not(cond1))
    elif(op == "xor"):
        c1 = bool(not(cond1) and cond2)
        c2 = bool(cond1 and not(cond2))
        c = bool(c1 or c2)
        return(c)
    else:
        raise(SyntaxError("not supported op: "+op))


def bool_funcs_ops(funcs,ops):
    def _rslt(funcs,ops,arg):
        rslts = []
        for i in range(len(funcs)):
            rslt = bool(funcs[i](arg))
            rslts.append(rslt)
        cond = rslts[0]
        for i in range(1,len(rslts)):
            op = ops[i-1]
            cond = bool_op(op,cond,rslts[i])
        return(cond)
    p = functools.partial(_rslt,funcs,ops)
    return(p)


####

def not_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        return(not(func(*args,**kwargs)))
    return(wrapper)

#####

def ifcall(cond,f,*args):
    rslt = None
    if(cond):
        rslt = f(*args)
    else:
        pass
    return(rslt)

def ifapply(cond,f,args):
    return(ifcall(cond,f,*args))

def ifnt_call(cond,f,*args):
    return(ifcall(not(cond),f,*args))

def ifnt_apply(cond,f,args):
    return(ifcall(not(cond),f,*args))

def if_calla_else_callb(cond,fa,fb,*args):
    rslt = None
    if(cond):
        rslt = fa(*args)
    else:
        rslt = fb(*args)
    return(rslt)


def if_applya_else_applyb(cond,fa,fb,args):
    return(if_calla_else_callb(cond,fa,fb,*args))

def ifnt_calla_else_callb(cond,fa,fb,*args):
    return(if_calla_else_callb(not(cond),fa,fb,*args))

def ifnt_applya_else_applyb(cond,fa,fb,args):
    return(if_calla_else_callb(not(cond),fa,fb,*args))


#####
