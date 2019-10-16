#jobj                 json-like-object ,supoort dict,list,tuple,set,recursive-embeded
#fpl                  full-path-list
#pl                   path-list,not-include-number
#tpl                  tag-path-list,not-include-number,not-include-number-string
#getfpl               getitem-via-fpl
#setfpl               setitem-via-fpl
#delfpl               delitem-via-fpl
#setdflt_fpl          set-default-item-via-fpl


import copy
import efuntool.efuntool as eftl
import elist.elist as elel


def getfpl(jobj,fpl):
    '''
        y = {'c': {'b': 200}}
        getfpl(y,['c','b'])
        >>>200
    '''
    this = jobj
    lngth = fpl.__len__()
    for i in range(0,lngth):
        key = fpl[i]
        this = this.__getitem__(key)
    return(this)


def setfpl(jobj,fpl,value):
    '''
        y = {'c': {'b': 250}}
        setfpl(y,['c','b'],200)
        y
        >>>200
    '''
    this = jobj
    lngth = fpl.__len__()-1
    for i in range(0,lngth):
        key = fpl[i]
        this = this.__getitem__(key)
    this.__setitem__(fpl[-1],value)
    return(jobj)


def delfpl(jobj,fpl):
    '''
        y = {'c': {'b': 200}}
        delfpl(y,['c','b'])
        >>>{'c': {}}
    '''
    this = jobj
    for i in range(0,fpl.__len__()-1):
        key = fpl[i]
        this = this.__getitem__(key)
    this.__delitem__(fpl[-1])
    return(jobj)


def setdflt_fpl(jobj,fpl,**kwargs):
    '''
        #if fpl already in jobj, will do nothing
        y = {}
        fpl = ['c','b']
        setdflt_fpl(y,fpl)
        y
        >>>{'c': {'b': {}}}
        setdflt_fpl(y,fpl)
        >>>{'c': {'b': {}}}
    '''
    dflt = eftl.dflt_kwargs("value",{},**kwargs)
    this = jobj
    for i in range(0,fpl.__len__()):
        key = fpl[i]
        try:
            this.__getitem__(key)
        except:
            try:
                # necessary ,when dflt = {} or []
                de = copy.deepcopy(dflt)
                this.__setitem__(key,de)
            except Exception as err:
                print(err)
                #return(jobj)
            else:
                pass
            this = this.__getitem__(key)
        else:
            this = this.__getitem__(key)
    return(jobj)


def _bracket_map_func(key):
    if(isinstance(key,str)):
        return("['"+str(key)+"']")
    else:
        return("["+str(key)+"]")

def fplgetbracket_path(fpl):
    fpl = elel.mapv(fpl,_bracket_map_func)
    s = elel.join(fpl,'')
    return(s)





