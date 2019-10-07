import os
from io import StringIO
import lxml.etree as lxe
import elist.elist as elel

from nvhtml import engine
from nvhtml import fs
from nvhtml import utils


def rootize(s,**kwargs):
    if('parse' in kwargs):
        f = StringIO(s)
        root = lxe.parse(f)
    elif('xml' in kwargs):
        root = lxml.etree.XML(s)
    elif('html' in kwargs):
        root = lxml.etree.HTML(s)
    else:
        try:
            root = lxe.HTML(s)
        except:
            try:
                root = lxml.etree.XML(s)
            except:
                f = StringIO(s)
                root = lxe.parse(f)
            else:
                pass
        else:
            pass
    return(root)

def xpath(s,xp,*args,**kwargs):
    root = rootize(s,**kwargs)
    all = root.xpath(xp)
    all = elel.mapv(all,engine.source,[])
    args = list(args)
    if(args.__len__() ==0):
        return(tuple(all))
    if(args.__len__() ==1):
        return(all[args[0]])
    else:
        return(tuple(elel.select_seqs(all,args)))

def xpath_levels(s,xp,*args,**kwargs):
    root = rootize(s,**kwargs)
    selected = engine.xpath_levels(root,xp,*args,**kwargs)
    selected = elel.mapv(selected,engine.source,[])
    return(selected)

def plget(s,*args,**kwargs):
    root = rootize(s,**kwargs)
    if("strict" in kwargs):
        strict = kwargs['strict']
    else:
        strict = True
    args = list(args)
    if(isinstance(args[0],list)):
        pl = args[0]
    else:
        pl = args
    xp = elel.join(pl,'/')
    if(strict):
        xp = "/" + xp
    else:
        xp = "//" + xp
    if('whiches' in kwargs):
        whiches = kwargs['whiches']
        if(isinstance(whiches,list)):
            pass
        else:
            whiches =[whiches]
    else:
        whiches = []
    return(xpath(s,xp,*whiches))

def wfs_traverse(s,**kwargs):
    root = rootize(s,**kwargs)
    handler = engine.WFS(root)
    return(handler)

def wfspls(s,**kwargs):
    root = rootize(s,**kwargs)
    pls = engine.wfspls(root)
    return(pls)

def edfs_traverse(s,**kwargs):
    root = rootize(s,**kwargs)
    handler = engine.EDFS()
    lxml.sax.saxify(root, handler)
    return(handler)

def edfspls(s,**kwargs):
    return(edfs_traverse(s,**kwargs).pls)

def textizenone(s):
    if(s == None):
        return("")
    else:
        return(s)

def fmt_comment_path(path):
    path = path.replace("\x20","#")
    path = path.replace("<","@lt")
    path = path.replace(">","@gt")
    return(path)

def save2file(d):
    path = utils.pl2path(d['dummy_pl'])
    path = "." + path 
    path = fmt_comment_path(path)
    if(os.path.exists(path)):
        pass
    else:
        os.makedirs(path)
    fs.wfile(path+"/tail",textizenone(d['tail']))
    fs.wfile(path+"/text",textizenone(d['text']))
    fs.wfile(path+"/text_intag",textizenone(d['text_intag']))
    fs.wjson(path+"/attrib",d['attrib'])

def todirs(s,**kwargs):
    root = rootize(s,**kwargs)
    unhandled = [{"node":root,"dummy_pl":[]}]
    next_unhandled = []
    while(unhandled.__len__()>0):
        pls = []
        for i in range(0,unhandled.__len__()):
            each_node = unhandled[i]['node']
            ppl = unhandled[i]['dummy_pl']
            childs = each_node.getchildren()
            pl = engine.pathlist(each_node)
            which = pls.count(pl)
            pls.append(pl)
            #dummy_pl = copy.copy(ppl)
            dummy_pl = elel.fcp(ppl)
            ###########################
            d = {}
            d['tag'] = str(each_node.tag)
            d['sibseq'] = engine.sibseq(each_node)
            d['attrib'] = dict(each_node.attrib)
            d['text'] = each_node.text
            d['tail'] = each_node.tail
            d['text_intag'] = engine.text_intag(each_node)
            dummy_pl.append(d['tag']+"_"+str(which))
            d['dummy_pl'] = dummy_pl
            save2file(d)
            childs = elel.mapv(childs,lambda child:({'node':child,"dummy_pl":d['dummy_pl']}),[])
            if(childs.__len__() == 0):
                pass
            else:
                next_unhandled = next_unhandled + childs
        unhandled = next_unhandled
        next_unhandled = []


def iter_text(ele):
    '''     <Why need itertext? >
        >>>html_text = '<html><body>TEXT<br/>TAIL</body></html>'
        >>>root = etree.HTML(html_text)
        >>>eles = root.xpath("//html/body")
        >>>eles[0].text
        'TEXT'
        >>>eles[0].tail == None
        True
        >>> nvbody.etree_get_text(eles[0])
        'TEXTTAIL'
        >>>
        >>>
        >>> eles = root.xpath("//html/body/br")
        >>> eles[0].text == None
        True
        >>> eles[0].tail
        'TAIL'
        >>> nvbody.etree_get_text(eles[0])
        ''
    >>>
    '''
    it = ele.itertext()
    texts = list(it)
    text = ''
    for i in range(0,texts.__len__()):
        text = text + texts[i]
    return(text)


