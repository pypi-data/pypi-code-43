import elist.elist as elel


def get_mros(obj):
    '''
        >>> a= 5
        >>> get_mros(a)
        [5,<class 'int'>, <class 'object'>]
        >>>
    '''
    if(hasattr(obj,'mro')):
        return(obj.mro())
    else:
        return([obj]+type(obj).mro())


def get_attrs_chain(obj):
    '''
        >>> class tst():
        ...     def __init__(self):
        ...         self._u = "_u"
        ...         self.u = "u"
        ...
        >>> t = tst()
        >>>
        >>> parr(get_attrs_chain(t))
        ['_u', 'u']
        ['__dict__', '__module__', '__weakref__']
        ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__']
        >>>
    '''
    mros = get_mros(obj)
    chain = elel.mapv(mros,get_all_attrs)
    st_chain = elel.mapv(chain,set)
    lngth = len(chain)
    owns = []
    for i in range(0,lngth-1):
        ownattrs = st_chain[i].difference(st_chain[i+1])
        owns.append(ownattrs)
    owns.append(st_chain[-1])
    owns = elel.mapv(owns,lambda st:elel.sort(list(st)))
    return(owns)

def get_own_attrs(obj):
    '''
        >>> class tst():
        ...     def __init__(self):
        ...         self._u = "_u"
        ...         self.u = "u"
        ...
        >>> t = tst()
        >>>
        >>> get_own_attrs(t)
        ['_u', 'u']
        >>>
    '''
    ownattrs_arr = get_attrs_chain(obj)
    return(ownattrs_arr[0])

def get_inherited_attrs(obj,*whiches):
    '''
        >>> class tst():
        ...     def __init__(self):
        ...         self._u = "_u"
        ...         self.u = "u"
        ...
        >>> t = tst()
        >>>
        >>> get_inherited_attrs(t,0)
        ['_u', 'u']
        >>>
        >>> get_inherited_attrs(t,1)
        ['__dict__', '__module__', '__weakref__']
        >>>
        >>> get_inherited_attrs(t,2)
        ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__']
        >>>
        >>> get_inherited_attrs(t,0,1)
        ['_u', 'u', '__dict__', '__module__', '__weakref__']
        >>>
    '''
    ownattrs_arr = get_attrs_chain(obj)
    rslt = elel.select_seqs(ownattrs_arr,whiches)
    rslt = elel.reduce_left(rslt,lambda acc,ele:acc+ele,[])
    if(len(rslt)==1):
        return(rslt[0])
    else:
        return(rslt)

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

def get_own_priv_attrs(obj):
    '''
        >>> class tst():
        ...     def __init__(self):
        ...         self._u = "_u"
        ...         self.u = "u"
        ...
        >>> t = tst()
        >>>
        >>> get_own_priv_attrs(t)
        ['_u']
        >>>
    '''
    attrs = get_own_attrs(obj)
    attrs = elel.cond_select_values_all(attrs,cond_func=lambda ele:(ele[0:2]!="__") and (ele.startswith("_")))
    return(attrs)

def get_own_builtin_attrs(obj):
    '''
        >>> class tst():
        ...     def __init__(self):
        ...         self._u = "_u"
        ...         self.u = "u"
        ...
        >>> t = tst()
        >>>
        >>> get_own_buildin_attrs(t)
        []
        >>>
    '''
    attrs = get_own_attrs(obj)
    attrs = elel.cond_select_values_all(attrs,cond_func=lambda ele:ele.startswith("__"))
    return(attrs)


def get_inherited_visible_attrs(obj,*whiches):
    '''
        >>> class tst():
        ...     def __init__(self):
        ...         self._u = "_u"
        ...         self.u = "u"
        ...
        >>> t = tst()
        >>>
        >>> get_inherited_visible_attrs(t,1)
        []
        >>>
    '''
    attrs = get_inherited_attrs(obj,*whiches)
    attrs = elel.cond_select_values_all(attrs,cond_func=lambda ele:not(ele.startswith("_")))
    return(attrs)

def get_inherited_priv_attrs(obj,*whiches):
    '''
        >>> class tst():
        ...     def __init__(self):
        ...         self._u = "_u"
        ...         self.u = "u"
        ...
        >>> t = tst()
        >>>
        >>> get_inherited_priv_attrs(t,1)
        []
        >>>
    '''
    attrs = get_inherited_attrs(obj,*whiches)
    attrs = elel.cond_select_values_all(attrs,cond_func=lambda ele:(ele[0:2]!="__") and (ele.startswith("_")))
    return(attrs)

def get_inherited_builtin_attrs(obj,*whiches):
    '''
        >>> class tst():
        ...     def __init__(self):
        ...         self._u = "_u"
        ...         self.u = "u"
        ...
        >>> t = tst()
        >>>
        >>> get_inherited_buildin_attrs(t,1)
        ['__dict__', '__module__', '__weakref__']
        >>>
        >>> get_inherited_builtin_attrs(t,2)
        ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__']
        >>>
    '''
    attrs = get_inherited_attrs(obj,*whiches)
    attrs = elel.cond_select_values_all(attrs,cond_func=lambda ele:ele.startswith("__"))
    return(attrs)
    

def get_all_attrs(obj):
    '''
        >>> a= 5
        >>> get_all_attrs(a)
        ['__abs__', '__add__', '__and__', '__bool__', '__ceil__', '__class__', '__delattr__', '__dir__', '__divmod__', '__doc__', '__eq__', '__float__', '__floor__', '__floordiv__', '__format__', '__ge__', '__getattribute__', '__getnewargs__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__invert__', '__le__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__', '__neg__', '__new__', '__or__', '__pos__', '__pow__', '__radd__', '__rand__', '__rdivmod__', '__reduce__', '__reduce_ex__', '__repr__', '__rfloordiv__', '__rlshift__', '__rmod__', '__rmul__', '__ror__', '__round__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__', '__rtruediv__', '__rxor__', '__setattr__', '__sizeof__', '__str__', '__sub__', '__subclasshook__', '__truediv__', '__trunc__', '__xor__', 'bit_length', 'conjugate', 'denominator', 'from_bytes', 'imag', 'numerator', 'real', 'to_bytes']
    '''
    return(dir(obj))

def get_all_visible_attrs(obj):
    '''
        >>> a = 5
        >>> get_all_visible_attrs(a)
        ['bit_length', 'conjugate', 'denominator', 'from_bytes', 'imag', 'numerator', 'real', 'to_bytes']
        >>>
    '''
    attrs = dir(obj)
    return(elel.cond_select_values_all(attrs,cond_func=lambda ele:not(ele.startswith("_"))))

def get_all_builtin_attrs(obj):
    '''
        >>> a = 5
        >>> get_all_builtin_attrs(a)
        ['__abs__', '__add__', '__and__', '__bool__', '__ceil__', '__class__', '__delattr__', '__dir__', '__divmod__', '__doc__', '__eq__', '__float__', '__floor__', '__floordiv__', '__format__', '__ge__', '__getattribute__', '__getnewargs__', '__gt__', '__hash__', '__index__', '__init__', '__init_subclass__', '__int__', '__invert__', '__le__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__', '__neg__', '__new__', '__or__', '__pos__', '__pow__', '__radd__', '__rand__', '__rdivmod__', '__reduce__', '__reduce_ex__', '__repr__', '__rfloordiv__', '__rlshift__', '__rmod__', '__rmul__', '__ror__', '__round__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__', '__rtruediv__', '__rxor__', '__setattr__', '__sizeof__', '__str__', '__sub__', '__subclasshook__', '__truediv__', '__trunc__', '__xor__']
    '''
    attrs = dir(obj)
    return(elel.cond_select_values_all(attrs,cond_func=lambda ele:ele.startswith("__")))

def get_all_priv_attrs(obj):
    '''
        class tst():
            def __init__(self):
                self._u = "_u"
                self.u = "u"
        
        t = tst()
        >>> get_all_priv_attrs(t)
        ['_u']
        >>>
    '''
    attrs = dir(obj)
    return(elel.cond_select_values_all(attrs,cond_func=lambda ele:(ele[0:2]!="__") and (ele.startswith("_"))))

