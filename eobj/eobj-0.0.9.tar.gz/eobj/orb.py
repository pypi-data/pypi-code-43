#orb
from   eobj.primitive import *
from   eobj.key_fplfuncs import getfpl as kgetfpl
from   eobj.key_fplfuncs import setfpl as ksetfpl
from   eobj.key_fplfuncs import delfpl as kdelfpl
import eobj.kastr as kastr


from efuntool.efuntool import ternaryop
import elist.elist as elel



_INTERNAL_ATTR_MAP = {
    "\x20":"fpl",
    "\x20\x20":"data",
    "fpl":"\x20",
    "data":"\x20\x20"
}

#'_ζ'   trick !!!
_INITED_ATTR_KEY = "_"+kastr.greece_md['zeta']






class Orb():
    def __init__(self):
        #Orb主要用来Tab显示,为了不被其他属性扰乱,所以不继承dict
        self._type = null
        self._data = undefined
        self._ζ = False
    def __repr__(self):
        cond = hasattr(self,"_ζ") and self._ζ and hasattr(self,_INTERNAL_ATTR_MAP["fpl"]) 
        if(cond):
            # 如果 已经被初始化,使用fpl真实的key-pathlist 去操作真实的数据
            fpl = self.__getattribute__(_INTERNAL_ATTR_MAP["fpl"])
            if(self._ptype == "set"):
                return(kgetfpl(self._im_pjobj,[fpl[-1]]).__repr__())
            else:
                return(kgetfpl(self._data,fpl).__repr__())
        else:
            return("")
    '''
    #########################################################
    # 因为list ,tuple 和 set 的删除方式需要单独写
    # list 要和 ltdict 对应,但是名称 需要是l0_,l1_,l2_...
    # set 需要单独写一个类似ltdict的库,名称需要是s0_,s1_,s2_
    # 所以暂时不支持同步的delete
    ########################################################
    def __delattr__(self,an):
        super().__delattr__(an)
        cond = (an != "_ζ") and (an != _INTERNAL_ATTR_MAP['fpl']) and hasattr(self,"_ζ") and self._ζ and hasattr(self,_INTERNAL_ATTR_MAP["fpl"]) 
        if(cond):
            #In detail,delete operation is operating on parent node
            #######
            pfpl = self.__getattribute__(_INTERNAL_ATTR_MAP["fpl"])
            fpl = elel.fcp(pfpl)
            kn = kastr.fatag2ftag(an)
            fpl.append(kn)
            kdelfpl(self._data,fpl)
            #############################
        else:
            pass
    '''
    '''
    ############################################################
    # 因为list ,tuple 和 set 的删除方式需要单独写
    # list 要和 ltdict 对应,但是名称 需要是l0_,l1_,l2_...
    # set 需要单独写一个类似ltdict的库,名称需要是s0_,s1_,s2_
    # 所以暂时不支持同步的set
    #############################################################
    def __setattr__(self,an,value):
        super().__setattr__(an,value)
        #### super trick!
        cond = (an != "_ζ") and (an != _INTERNAL_ATTR_MAP['fpl']) and hasattr(self,"_ζ") and self._ζ and hasattr(self,_INTERNAL_ATTR_MAP["fpl"]) 
        if(cond):
            #In detail,delete operation is operating on parent node
            pfpl = self.__getattribute__(_INTERNAL_ATTR_MAP["fpl"])
            fpl = elel.fcp(pfpl)
            kn = kastr.fatag2ftag(an)
            fpl.append(kn)
            if(self._ptype == "set"):
                #找到parent
                #parent_data = kgetfpl(self._data,fpl)
            else:
                ksetfpl(self._data,fpl,value)
        else:
            pass
    '''

def is_dflt_orb(orb):
    return(ternaryop(orb._type==null,True,False))
