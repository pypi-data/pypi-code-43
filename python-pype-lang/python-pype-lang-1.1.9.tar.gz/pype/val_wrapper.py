import pprint as pp
from copy import deepcopy
from _operator import *

is_dict=lambda x: isinstance(x,dict)
is_list=lambda x: isinstance(x,list)
is_set=lambda x: isinstance(x,set)

def is_scalar(x):

    return isinstance(x,float) \
        or isinstance(x,int) \
        or (isinstance(x,ValWrapper) and is_scalar(x.val))


def val_wrapper(val):

    if not isinstance(val,ValWrapper):

        return ValWrapper(val)

    return val


def get_val(obj):

    if isinstance(obj,ValWrapper):

        obj=obj.val

    if is_list(obj):

        return [get_val(el) for el in obj]

    if is_set(obj):

        return {get_val(el) for el in obj}

    if is_dict(obj):

        return {k:get_val(v) \
                for (k,v) in obj.items()}

    return obj


def apply_scalar_operator(operator,scalar,obj):

    scalar=get_val(scalar)
    obj=get_val(obj)

    if is_list(obj):

        return [apply_scalar_operator(operator,scalar,v) for v in obj]

    if is_set(obj):

        return {apply_scalar_operator(operator,scalar,v) for v in obj}

    if is_dict(obj):

        return {k:apply_scalar_operator(operator,scalar,v) \
                for (k,v) in obj.items()}

    return operator(scalar,obj)


def apply_multi_scalar_operator(operator,obj1,obj2):
    '''
    This is for when obj1 contains scalars that are multiplied with scalars in obj2.
    '''
    obj1=get_val(obj1)
    obj2=get_val(obj2)

    if is_list(obj1):

        return [apply_scalar_operator(operator,el1,el2)\
                for (el1,el2) in zip(obj1,obj2)]

    if is_set(obj1):

        return {apply_scalar_operator(operator,el1,el2)\
                for (el1,el2) in zip(obj1,obj2)}

    if is_dict(obj1):

        keys=set(obj1.keys())&set(obj2.keys())

        return {k:apply_scalar_operator(operator,obj1[k],obj2[k]) \
                for k in keys}

    return apply_scalar_operator(operator,obj1,obj2)


def apply_operator(operator,obj1,obj2):
    '''
    We are assuming obj1 and obj2 have exactly the same structure.
    '''
    obj1=get_val(obj1)
    obj2=get_val(obj2)

    if is_list(obj1):

        return [apply_operator(operator,el1,el2) \
                for (el1,el2) in zip(obj1,obj2)]

    if is_dict(obj1):

        keys=set(obj1.keys())&set(obj2.keys())

        return {k:apply_operator(operator,obj1[k],obj2[k]) for k in keys}

    if is_set(obj1):

        return {apply_operator(operator,el1,el2) \
                for (el1,el2) in zip(obj1,obj2)}

    return operator(obj1,obj2)


class ValWrapper(object):
    '''
    Overrides operators so that you can do arithmetic on values of dictionaries
    with the same structure.  They must have exactly the same structure, no exceptions.
    '''
    def __init__(self,val):

        if is_list(val):

            self.val=[ValWrapper(el) for el in list]

        elif is_dict(val):

            self.val={k:ValWrapper(v) for (k,v) in val.items()}

        elif is_set(val):

            self.val={ValWrapper(v) for v in val}

        else:

            self.val=val


    def _apply(self,operator,otherObj):

        val=deepcopy(self.val)
        otherObj=deepcopy(otherObj)

        # If the valWrapper is a scalar, then apply the operator to 
        # every scalar value in otherObj

        if is_scalar(val):

            val=apply_scalar_operator(operator,val,otherObj)

        elif is_dict(val) and any([is_scalar(v) for (k,v) in val.items()]):

            val=apply_multi_scalar_operator(operator,val,otherObj)
                
        # Otherwise, otherObj must have the exact same structure as self.val
        else:

            val=apply_operator(operator,val,otherObj)

        return ValWrapper(val)


    def get_val(self):

        return get_val(self)


    def __add__(self,otherObj):

        return self._apply(add,otherObj)


    def __radd__(self,otherObj):

        otherObj=val_wrapper(otherObj)

        return otherObj._apply(add,otherObj)


    def __sub__(self,otherObj):

        return self._apply(sub,otherObj)


    def __rsub__(self,otherObj):

        otherObj=val_wrapper(otherObj)

        return otherObj._apply(sub,self)


    def __mul__(self,otherObj):

        return self._apply(mul,otherObj)


    def __rmul__(self,otherObj):

        otherObj=val_wrapper(otherObj)

        return self._apply(mul,otherObj)


    def __truediv__(self,otherObj):

        '''
        print('*'*30)
        print('applying truediv')
        pp.pprint(self.get_val())
        print(f'is self')
        pp.pprint(otherObj.get_val())
        print(f'is otherObj')
        pp.pprint(self._apply(truediv,otherObj).get_val())
        '''

        return self._apply(truediv,val_wrapper(1e-100)+otherObj)


    def __rtruediv__(self,otherObj):

        otherObj=val_wrapper(otherObj)

        return otherObj._apply(truediv,val_wrapper(1e-100)+self)


    def __repr__(self):

        return f'ValWrapper({str(self.val)})'



                
if __name__=='__main__':

    d1=ValWrapper({0:1,1:2})
    d2={0:3,1:4}
        
    print(f'{d1+d2} is d1+d2')

    d3=ValWrapper({0:{0:1},1:{3:4}})
    d4={0:{0:1},1:{3:2}}

    print(f'{d4+d3} is d1+d2')

    d5=ValWrapper({0:{0:1},1:{3:4}})
    d6={0:{0:1},1:{3:2}}

    print(f'{d5-d6} is d5-d6')

    d7=ValWrapper({0:{0:1},1:{3:4}})
    d8={0:{0:2},1:{3:6}}

    print(f'{d7/d8} is d7/d8')

    d10={0:{1:2,3:4},1:{5:6,7:{11:9,12:3}}}
    s=ValWrapper(3)

    print(f'{s*d10} is s*d10')

    d9=ValWrapper({0:3,1:4})
    d10={0:{1:2,3:4},1:{5:6,7:{11:9,12:3}}}

    print(f'{d9*d10} is d9*d10')

    d10=ValWrapper({0:{1:2,3:4},1:{5:6,7:{11:9,12:3}}})

    print(f'{1-d10} is 1-d10')
