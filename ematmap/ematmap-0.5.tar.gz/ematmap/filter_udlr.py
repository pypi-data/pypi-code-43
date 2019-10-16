import ematmap.filter_engine as engine

@engine.udlr_wrap
def ffltre(d):
    return(engine.ffltre(d))


@engine.udlr_wrap
def xfltre(d):
    return(engine.xfltre(d))


@engine.udlr_wrap
def yfltre(d):
    return(engine.yfltre(d))


@engine.udlr_wrap
def vfltre(d):
    return(engine.vfltre(d))


@engine.udlr_wrap
def ofltre(d):
    return(engine.ofltre(d))


@engine.udlr_wrap
def fxfltre(d):
    return(engine.fxfltre(d))


@engine.udlr_wrap
def fyfltre(d):
    return(engine.fyfltre(d))


@engine.udlr_wrap
def fvfltre(d):
    return(engine.fvfltre(d))


@engine.udlr_wrap
def fofltre(d):
    return(engine.fofltre(d))


@engine.udlr_wrap
def xyfltre(d):
    return(engine.xyfltre(d))


@engine.udlr_wrap
def xvfltre(d):
    '''
        >>> xvfltre([[1],[2,3]],cond_func=lambda x,v:(v%2==1))
        [1, 3]
        >>>
    '''
    return(engine.xvfltre(d))


@engine.udlr_wrap
def xofltre(d):
    return(engine.xofltre(d))


@engine.udlr_wrap
def yvfltre(d):
    return(engine.yvfltre(d))


@engine.udlr_wrap
def yofltre(d):
    return(engine.yofltre(d))


@engine.udlr_wrap
def vofltre(d):
    return(engine.vofltre(d))


@engine.udlr_wrap
def fxyfltre(d):
    return(engine.fxyfltre(d))


@engine.udlr_wrap
def fxvfltre(d):
    return(engine.fxvfltre(d))


@engine.udlr_wrap
def fxofltre(d):
    return(engine.fxofltre(d))


@engine.udlr_wrap
def fyvfltre(d):
    return(engine.fyvfltre(d))


@engine.udlr_wrap
def fyofltre(d):
    return(engine.fyofltre(d))


@engine.udlr_wrap
def fvofltre(d):
    return(engine.fvofltre(d))


@engine.udlr_wrap
def xyvfltre(d):
    return(engine.xyvfltre(d))


@engine.udlr_wrap
def xyofltre(d):
    return(engine.xyofltre(d))


@engine.udlr_wrap
def xvofltre(d):
    return(engine.xvofltre(d))


@engine.udlr_wrap
def yvofltre(d):
    return(engine.yvofltre(d))


@engine.udlr_wrap
def fxyvfltre(d):
    return(engine.fxyvfltre(d))


@engine.udlr_wrap
def fxyofltre(d):
    return(engine.fxyofltre(d))


@engine.udlr_wrap
def fxvofltre(d):
    return(engine.fxvofltre(d))


@engine.udlr_wrap
def fyvofltre(d):
    return(engine.fyvofltre(d))


@engine.udlr_wrap
def xyvofltre(d):
    return(engine.xyvofltre(d))


@engine.udlr_wrap
def fxyvofltre(d):
    return(engine.fxyvofltre(d))


#####
#####

def ffltrxy(m,**kwargs):
    return(ffltre(m,rtrn='loc',**kwargs))

def xfltrxy(m,**kwargs):
    return(xfltre(m,rtrn='loc',**kwargs))

def yfltrxy(m,**kwargs):
    return(yfltre(m,rtrn='loc',**kwargs))

def vfltrxy(m,**kwargs):
    return(vfltre(m,rtrn='loc',**kwargs))

def ofltrxy(m,**kwargs):
    return(ofltre(m,rtrn='loc',**kwargs))

def fxfltrxy(m,**kwargs):
    return(fxfltre(m,rtrn='loc',**kwargs))

def fyfltrxy(m,**kwargs):
    return(fyfltre(m,rtrn='loc',**kwargs))

def fvfltrxy(m,**kwargs):
    return(fvfltre(m,rtrn='loc',**kwargs))

def fofltrxy(m,**kwargs):
    return(fofltre(m,rtrn='loc',**kwargs))

def xyfltrxy(m,**kwargs):
    return(xyfltre(m,rtrn='loc',**kwargs))

def xvfltrxy(m,**kwargs):
    return(xvfltre(m,rtrn='loc',**kwargs))

def xofltrxy(m,**kwargs):
    return(xofltre(m,rtrn='loc',**kwargs))

def yvfltrxy(m,**kwargs):
    return(yvfltre(m,rtrn='loc',**kwargs))

def yofltrxy(m,**kwargs):
    return(yofltre(m,rtrn='loc',**kwargs))

def vofltrxy(m,**kwargs):
    return(vofltre(m,rtrn='loc',**kwargs))

def fxyfltrxy(m,**kwargs):
    return(fxyfltre(m,rtrn='loc',**kwargs))

def fxvfltrxy(m,**kwargs):
    return(fxvfltre(m,rtrn='loc',**kwargs))

def fxofltrxy(m,**kwargs):
    return(fxofltre(m,rtrn='loc',**kwargs))

def fyvfltrxy(m,**kwargs):
    return(fyvfltre(m,rtrn='loc',**kwargs))

def fyofltrxy(m,**kwargs):
    return(fyofltre(m,rtrn='loc',**kwargs))

def fvofltrxy(m,**kwargs):
    return(fvofltre(m,rtrn='loc',**kwargs))

def xyvfltrxy(m,**kwargs):
    return(xyvfltre(m,rtrn='loc',**kwargs))

def xyofltrxy(m,**kwargs):
    return(xyofltre(m,rtrn='loc',**kwargs))

def xvofltrxy(m,**kwargs):
    return(xvofltre(m,rtrn='loc',**kwargs))

def yvofltrxy(m,**kwargs):
    return(yvofltre(m,rtrn='loc',**kwargs))

def fxyvfltrxy(m,**kwargs):
    return(fxyvfltre(m,rtrn='loc',**kwargs))

def fxyofltrxy(m,**kwargs):
    return(fxyofltre(m,rtrn='loc',**kwargs))

def fxvofltrxy(m,**kwargs):
    return(fxvofltre(m,rtrn='loc',**kwargs))

def fyvofltrxy(m,**kwargs):
    return(fyvofltre(m,rtrn='loc',**kwargs))

def xyvofltrxy(m,**kwargs):
    return(xyvofltre(m,rtrn='loc',**kwargs))

def fxyvofltrxy(m,**kwargs):
    return(fxyvofltre(m,rtrn='loc',**kwargs))

