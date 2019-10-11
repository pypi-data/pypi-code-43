import eobj.kfplnd as kfplnd 
import eobj.attr_fplfuncs  as afplfuncs
import eobj.key_fplfuncs as kfplfuncs
import eobj.pathlist_funcs  as plfuncs
import eobj.kastr as kastr
from   eobj.primitive import *
import eobj.wfsmat as wfsmat
import eobj.orb as orb
from   eobj.key_fplfuncs import fplgetbracket_path

import efuntool.etypetool as ettl
import ematmap.ematmap as emem
import elist.elist as elel


def set_ele_fatag(ele,wfsm):
    ptype = wfsmat.get_pele_via_ele(ele,wfsm)['type']
    ftag = ele.ftag
    ele.fatag = kastr.ftag2fatag(ftag,ptype)
    return(ele)

def set_wfsm_fatag(wfsm):
    wfsm[0][0].fatag = null
    emem.mapv(wfsm[1:],map_func=set_ele_fatag,other_args=[wfsm],inplace=True)
    return(wfsm)

def set_ele_fapl(ele,wfsm):
    pfapl = wfsmat.get_pele_via_ele(ele,wfsm).fapl
    fatag = ele.fatag
    fapl = plfuncs.ppl2pl(fatag,pfapl)
    ele.fapl = fapl
    return(ele)

def set_ele_dotpath(ele):
    ele.dotpath = elel.join(ele.fapl,'.')
    return(ele)



def set_wfsm_fapl(wfsm):
    wfsm[0][0].fapl = []
    emem.mapv(wfsm[1:],map_func=set_ele_fapl,other_args=[wfsm],inplace=True)
    return(wfsm)

def set_ele_typel(ele,wfsm):
    ptypel = wfsmat.get_pele_via_ele(ele,wfsm).typel
    type = ele['type']
    typel = plfuncs.ppl2pl(type,ptypel)
    ele.typel = typel
    return(ele)


def set_wfsm_typel(wfsm):
    wfsm[0][0].typel = [wfsm[0][0]['type']]
    emem.mapv(wfsm[1:],map_func=set_ele_typel,other_args=[wfsm],inplace=True)
    return(wfsm)


def set_wfsm_dotpath(wfsm):
    emem.mapv(wfsm,map_func=set_ele_dotpath,inplace=True)
    return(wfsm)


def jobj2wfsm(jobj):
    wfsm = kfplnd.get_jobj_wfsmat(jobj)
    wfsm = set_wfsm_fatag(wfsm)
    wfsm = set_wfsm_fapl(wfsm)
    wfsm = set_wfsm_typel(wfsm)
    wfsm = set_wfsm_dotpath(wfsm)
    return(wfsm)



def wfsm2orb(wfsm,jobj):
    o = orb.Orb()
    eles = wfsmat.wfs_eles(wfsm)
    fpls = elel.mapv(eles,lambda ele:ele.fpl)
    fapls = elel.mapv(eles,lambda ele:ele.fapl)
    tpls = elel.mapv(eles,lambda ele:ele['type'])
    ptpls = elel.mapv(eles,lambda ele:ele['ptype'])
    #im_pjobj  intermediate-pjobj 例如set 对应成list
    impjobjs = elel.mapv(eles,lambda ele:ele['im_pjobj'])
    for i in range(len(fapls)):
        fapl = fapls[i]
        fpl = fpls[i]
        tp = tpls[i]
        ptp = ptpls[i]
        pjobj = impjobjs[i]
        dflt = orb.Orb()
        del dflt._data
        #super trick!
        dflt.__setattr__(orb._INTERNAL_ATTR_MAP['fpl'],fpl)
        dflt.__setattr__('_data',jobj)
        dflt.__setattr__('_type',tp)
        dflt.__setattr__('_ptype',ptp)
        dflt.__setattr__('_im_pjobj',pjobj)
        afplfuncs.setdflt_fpl(o,fapl,value=dflt,_inited=True)
    #this is a trick
    o._ζ = True
    return(o)

def jobj2orb(jobj):
    wfsm = jobj2wfsm(jobj)
    o = wfsm2orb(wfsm,jobj)
    o._wfsm = wfsm
    o._data = jobj
    o._type = wfsm[0][0]['type']
    o._ptype = wfsm[0][0]['ptype']
    o._im_pjobj = wfsm[0][0]['im_pjobj']
    o.__setattr__(orb._INTERNAL_ATTR_MAP['fpl'],[])
    return(o)


def wfstree(o,*args):
    lngth = len(args)
    #njobj = o._data
    #wfsm = jobj2wfsm(njobj)
    wfsm = o._wfsm
    depth = len(wfsm)
    start = elel.uniform_index(args[0],depth+1) if(lngth>0) else  0
    end = elel.uniform_index(args[1],depth+1) if(lngth>1) else (depth+1)
    dotpm = emem.mapv(wfsm,map_func=lambda ele:ele.dotpath)
    dotpm = dotpm[start:end]
    for row in dotpm:
        for each in row:
            print(each)


def sdfstree(o,*args):
    lngth = len(args)
    wfsm = o._wfsm
    depth = len(wfsm)
    start = elel.uniform_index(args[0],depth+1) if(lngth>0) else  0
    end = elel.uniform_index(args[1],depth+1) if(lngth>1) else (depth+1)
    sdfsel = wfsmat.m2sdfsel(wfsm)
    sdfsel = elel.cond_select_values_all(sdfsel,cond_func=lambda ele:(len(ele.fapl)>=start) and (len(ele.fapl)<end))
    sdfs = elel.mapv(sdfsel,lambda ele:ele.dotpath)
    for dotpath in sdfs:
        print(dotpath)



def edfstree(o,*args):
    lngth = len(args)
    wfsm = o._wfsm
    depth = len(wfsm)
    start = elel.uniform_index(args[0],depth+1) if(lngth>0) else  0
    end = elel.uniform_index(args[1],depth+1) if(lngth>1) else (depth+1)
    edfsel = wfsmat.m2edfsel(wfsm)
    edfsel = elel.cond_select_values_all(edfsel,cond_func=lambda ele:(len(ele.fapl)>=start) and (len(ele.fapl)<end))
    edfs = elel.mapv(edfsel,lambda ele:ele.dotpath)
    for dotpath in edfs:
        print(dotpath)




def wfsmget_wfsdotpaths(wfsm):
    wfsel = wfsmat.m2wfsel(wfsm)
    wfs_dotps = elel.mapv(wfsel,lambda ele:ele.dotpath)
    return(wfs_dotps)


def jobjget_wfsdotpaths(jobj):
    wfsm = jobj2wfsm(jobj)
    wfs_dotps = wfsmget_wfsdotpaths(wfsm)
    return(wfs_dotps)


def wfsmget_sdfsdotpaths(wfsm):
    sdfsel = wfsmat.m2sdfsel(wfsm)
    sdfs_dotps = elel.mapv(sdfsel,lambda ele:ele.dotpath)
    return(sdfs_dotps)


def jobjget_sdfsdotpaths(jobj):
    wfsm = jobj2wfsm(jobj)
    sdfs_dotps = wfsmget_sdfsdotpaths(wfsm)
    return(sdfs_dotps)


def wfsmget_edfsdotpaths(wfsm):
    edfsel = wfsmat.m2edfsel(wfsm)
    edfs_dotps = elel.mapv(edfsel,lambda ele:ele.dotpath)
    return(edfs_dotps)


def jobjget_edfsdotpaths(jobj):
    wfsm = jobj2wfsm(jobj)
    edfs_dotps = wfsmget_edfsdotpaths(wfsm)
    return(edfs_dotps)

###

def wfsmget_wfs_bracket_path(wfsm):
    wfsel = wfsmat.m2wfsel(wfsm)
    wfs_bracket_path = elel.mapv(wfsel,lambda ele:fplgetbracket_path(ele.fpl))
    return(wfs_bracket_path)

def wfsmget_sdfs_bracket_path(wfsm):
    sdfsel = wfsmat.m2sdfsel(wfsm)
    sdfs_bracket_path = elel.mapv(sdfsel,lambda ele:fplgetbracket_path(ele.fpl))
    return(sdfs_bracket_path)


def wfsmget_edfs_bracket_path(wfsm):
    edfsel = wfsmat.m2edfsel(wfsm)
    edfs_bracket_path = elel.mapv(edfsel,lambda ele:fplgetbracket_path(ele.fpl))
    return(edfs_bracket_path)


def jobjget_wfs_bracket_path(jobj):
    wfsm = jobj2wfsm(jobj)
    return(wfsmget_wfs_bracket_path(wfsm))

def jobjget_sdfs_bracket_path(jobj):
    wfsm = jobj2wfsm(jobj)
    return(wfsmget_sdfs_bracket_path(wfsm))

def jobjget_edfs_bracket_path(jobj):
    wfsm = jobj2wfsm(jobj)
    return(wfsmget_edfs_bracket_path(wfsm))

############################################

def wfs_brackets(o,*args):
    lngth = len(args)
    wfsm = o._wfsm
    depth = len(wfsm)
    start = elel.uniform_index(args[0],depth+1) if(lngth>0) else  0
    end = elel.uniform_index(args[1],depth+1) if(lngth>1) else (depth+1)
    wfsel = wfsmat.m2wfsel(wfsm)
    wfsel = elel.cond_select_values_all(wfsel,cond_func=lambda ele:(len(ele.fapl)>=start) and (len(ele.fapl)<end))
    wfs = elel.mapv(wfsel,lambda ele:fplgetbracket_path(ele.fpl))
    for each in wfs:
        print(each)




def sdfs_brackets(o,*args):
    lngth = len(args)
    wfsm = o._wfsm
    depth = len(wfsm)
    start = elel.uniform_index(args[0],depth+1) if(lngth>0) else  0
    end = elel.uniform_index(args[1],depth+1) if(lngth>1) else (depth+1)
    sdfsel = wfsmat.m2sdfsel(wfsm)
    sdfsel = elel.cond_select_values_all(sdfsel,cond_func=lambda ele:(len(ele.fapl)>=start) and (len(ele.fapl)<end))
    sdfs = elel.mapv(sdfsel,lambda ele:fplgetbracket_path(ele.fpl))
    for each in sdfs:
        print(each)


def edfs_brackets(o,*args):
    lngth = len(args)
    wfsm = o._wfsm
    depth = len(wfsm)
    start = elel.uniform_index(args[0],depth+1) if(lngth>0) else  0
    end = elel.uniform_index(args[1],depth+1) if(lngth>1) else (depth+1)
    edfsel = wfsmat.m2edfsel(wfsm)
    edfsel = elel.cond_select_values_all(edfsel,cond_func=lambda ele:(len(ele.fapl)>=start) and (len(ele.fapl)<end))
    edfs = elel.mapv(edfsel,lambda ele:ele.dotpath)
    for each in edfs:
        print(each)
