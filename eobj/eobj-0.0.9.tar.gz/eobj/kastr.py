from urllib.parse import quote,unquote
from estring.consts import greece_md,greece_upperch
from estring.estring import is_int_str,is_float_str
import re
from efuntool.ebooltool import blor_rtrn_first
from efuntool.etypetool import is_number

#####
def rplc(s,d):
    for k in d:
        s = s.replace(k,d[k])
    return(s)


stp2eip_d = {
    "%20":greece_md["epsilon"],
    "%09":greece_md["iota"],
    "%23":greece_md["pi"]
}

#stp          space-tab-pound
#eip          epsilon-iota-pi

def stp2eip(s):
    '''
        stp2eip_d = {
         '%20': 'ε',
         '%09': 'ι',
         '%23': 'π',
        }
        >>> stp2eip("name%20age")
        'nameεage'
        >>>
    '''
    s = rplc(s,stp2eip_d)
    return(s)

ddppu2tolpt_d = {
    "-":greece_md["theta"],
    ".":greece_md["omega"],
    "_":greece_md["lambda"],
    "%":greece_md["psi"],
    "/":greece_md["tau"]
}

#ddppu        dash-dot-path-percent-underscore
#tolpt        theta-omega-lambda-psi-tau

def ddppu2tolpt(s):
    '''
        ddppu2tolpt_d =  {
         '-': 'θ',
         '.': 'ω',
         '_': 'λ',
         '%': 'ψ',
         '/': 'τ'
        }
        >>> ddppu2tolpt("name%25age")
        'nameψ25age'
    '''
    s = rplc(s,ddppu2tolpt_d)
    return(s)

def initnum2rho(s):
    '''
        init-number to rho + s
        initnum2rho("1e3r")
        'ρ1e3r'
    '''
    rho = greece_md["rho"]
    cond = is_int_str(s[0])
    s = rho+s if(cond) else s
    return(s)


def key2attr(k):
    '''
        1.先urlib quote key
        2.空格,\t,# 转换
        3.横岗,点,下划线,百分号,路径转换
        4.数字开头转换
        >>> key2attr("name")
        'name'
        >>> key2attr("1name")
        'ρ1name'
        >>> key2attr("name-and-age")
        'nameθandθage'
        >>> key2attr("name age")
        'nameεage'
        >>> key2attr("name#age")
        'nameπage'
        >>>
        >>> key2attr("name&age")
        'nameψ26age'
        >>>
        >>> key2attr("name_age")
        'nameλage'
        >>>
    '''
    s = quote(k)
    s = stp2eip(s)
    s = ddppu2tolpt(s)
    s = initnum2rho(s)
    return(s)


#########

def rho2initnum(s):
    rho = greece_md["rho"]
    cond = is_int_str(s[0])
    s = s[1:] if(cond) else s
    return(s)

tolpt2ddppu_d = {
    greece_md["theta"]:"-",
    greece_md["omega"]:".",
    greece_md["lambda"]:"_",
    greece_md["psi"]:"%",
    greece_md["tau"]:"/"
}

def tolpt2ddppu(s):
    '''
        tolpt2ddppu_d =  {
         'θ': '-',
         'ω': '.',
         'λ': '_',
         'ψ': '%',
         'τ': '/',
        }
        >>> tolpt2ddppu('nameψ25age')
        'name%25age'
    '''
    s = rplc(s,tolpt2ddppu_d)
    return(s)

eip2stp_d = {
    greece_md["epsilon"]:"%20",
    greece_md["iota"]:"%09",
    greece_md["pi"]:"%23"
}

def eip2stp(s):
    '''
        eip2stp_d = {
         'ε': '%20',
         'ι': '%09',
         'π': '%23'
        }
        >>> eip2stp('nameεage')
        'name%20age'
        >>>
    '''
    s = rplc(s,eip2stp_d)
    return(s)


def attr2key(s):
    '''
        把特殊的希腊字母符号还原成原始key中的符号
        >>> attr2key("name")
        'name'
        >>> attr2key('ρ1name')
        'ρ1name'
        >>> attr2key('nameθandθage')
        'name-and-age'
        >>> attr2key('nameεage')
        'name age'
        >>> attr2key('nameπage')
        'name#age'
        >>> attr2key('nameψ26age')
        'name&age'
        >>> attr2key('nameλage')
        'name_age'
        >>>
    '''
    s = rho2initnum(s)
    s = tolpt2ddppu(s)
    s = eip2stp(s)
    s = unquote(s)
    return(s)


######################

def ftag2fatag(ftag,ptype):
    '''
        list  l<n>_
        tuple t<n>_
        set   s<n>_
        ptype can only be ['dict','list','tuple','set']
        dict[2]     σ2         greece_md['sigma']
        dict["2"]            
    '''
    if(ptype == "list"):
        fatag = "l"+str(ftag)+"_"
    elif(ptype == "tuple"):
        fatag = "t"+str(ftag)+"_"
    elif(ptype == "set"):
        fatag = "s"+str(ftag)+"_"
    else:
        if(is_number(ftag)):
            '''
                纯数字
            '''
            fatag = greece_md['sigma'] + str(ftag)
        else:
            fatag = key2attr(ftag)
    return(fatag)


def dcd_fatag(fatag,regex):
    m = regex.search(fatag)
    rslt = False if(m==None) else int(m.group(1))
    return(rslt)

def dcd_lfatag(fatag):
    regex = re.compile("l([0-9]+)_")
    return(dcd_fatag(fatag,regex))

def dcd_tfatag(fatag):
    regex = re.compile("t([0-9]+)_")
    return(dcd_fatag(fatag,regex))

def dcd_sfatag(fatag):
    regex = re.compile("s([0-9]+)_")
    return(dcd_fatag(fatag,regex))

def dcd_dfatag(fatag):
    '''
        >>> dcd_dfatag("σ1")
        1
        >>> dcd_dfatag("σ1.3")
        1.3
    '''
    regex = re.compile(greece_md['sigma']+"(.*)")
    m = regex.search(fatag)
    if(m==None):
        ftag = attr2key(fatag)
        return(ftag)
    else:
        n = m.group(1)
        n = int(n) if(is_int_str(n)) else float(n)
        return(n)


def fatag2ftag(fatag):
    '''
        list  l<n>_
        tuple t<n>_
        set   s<n>_
        dict  
    '''
    ftag = blor_rtrn_first(
        dcd_lfatag(fatag),
        dcd_tfatag(fatag),
        dcd_sfatag(fatag),
        dcd_dfatag(fatag),
        flses=[False]
    )
    return(ftag)
    


