from eobj.orb import Orb

import copy
import efuntool.efuntool as eftl



def getfpl(orb,fpl):
    '''
        orb = Orb()
        orb.html = Orb()
        orb.html.head = Orb()
        orb.html.body = Orb()
        orb.html.body.div = Orb()
        orb.html.body.div.text_ = "text"
        orb.html.body.div.tail_ = "tail"
        orb.html.body.div.attribs_ = Orb()
        orb.html.body.div.attribs_.cls = "ng-click"
        orb.html.body.div.attribs_.id = "ng0"
        >>> getfpl(orb,['html','body','div','text_'])
        'text'
        >>>
    '''
    this = orb
    lngth = fpl.__len__()
    for i in range(0,lngth):
        key = fpl[i]
        this = this.__getattribute__(key)
    return(this)


def setfpl(orb,fpl,value):
    '''
        >>>
        >>> setfpl(orb,['html','body','div','text_'],"new text")
        
        >>> getfpl(orb,['html','body','div','text_'])
        'new text'
        >>>
        fpl =[] 表示本身,不可通过此函数设置
    '''
    this = orb
    lngth = fpl.__len__()-1
    for i in range(0,lngth):
        key = fpl[i]
        this = this.__getattribute__(key)
    this.__setattr__(fpl[-1],value)
    return(orb)


def delfpl(orb,fpl):
    '''
        >>> delfpl(orb,['html','body','div','text_'])
        
        >>> getfpl(orb,['html','body','div','text_'])
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "<stdin>", line 11, in getfpl
        AttributeError: 'Orb' object has no attribute 'text_'
        >>>
    '''
    this = orb
    for i in range(0,fpl.__len__()-1):
        key = fpl[i]
        this = this.__getattribute__(key)
    this.__delattr__(fpl[-1])
    return(orb)


def setdflt_fpl(orb,fpl,**kwargs):
    '''
        #if fpl already in orb, will do nothing
        >>>
        >>> getfpl(orb,['html','body','div','text_'])
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "<stdin>", line 11, in getfpl
        AttributeError: 'Orb' object has no attribute 'text_'
        >>>
        >>>
        >>> setdflt_fpl(orb,['html','body','div','text_'])
        >>> getfpl(orb,['html','body','div','text_'])
        >>>
    '''
    dflt = eftl.dflt_kwargs("value",Orb(),**kwargs)
    this = orb
    for i in range(0,fpl.__len__()):
        key = fpl[i]
        try:
            this.__getattribute__(key)
        except:
            try:
                # necessary ,when dflt = {} or []
                de = copy.deepcopy(dflt)
                this.__setattr__(key,de)
            except Exception as e:
                print(e)
                #return(orb)
            else:
                pass
            this = this.__getattribute__(key)
        else:
            this = this.__getattribute__(key)
    ###this is a trick for jobj#
    _inited = eftl.dflt_kwargs("_inited",True,**kwargs)
    if(_inited):
        try:
            this._ζ = True
        except Exception as e:
            pass 
        else:
            pass
    else:
        pass
    ###############################
    return(orb)


