#ind     internal-node        for-internal-using  inherit-from-dict
#anl     attr_name_list
import efuntool.efuntool as eftl
from eobj.primitive import *
import types


class Node(dict):
    def __init__(self,anl,*args,**kwargs):
        '''
            nd = Node(['pl'],[['a','b']])
            >>> nd.pl
            ['a', 'b']
            nd = Node(['pl'])
            >>> nd.pl
            undefined
        '''
        args_lngth = len(args)
        dfltl= [undefined]*len(anl) if(args_lngth == 0) else args[0]
        eftl.self_kwargs(self,anl,dfltl,**kwargs)


def add_method_to_inst(inst,func,*args):
    fname = eftl.optional_arg(func.__name__,*args)
    f = types.MethodType(func,inst)
    inst.__setattr__(fname,f)
    return(inst)

def add_method_to_cls(cls,func,*args):
    return(add_method_to_inst(cls,func,*args))


def shcmmn(ele,attrs):
    for i in range(len(attrs)):
        v = ele.__getattribute__(attrs[i])
        print(attrs[i]," . ",v)

