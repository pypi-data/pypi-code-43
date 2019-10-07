
'''
    Toolset for lxml

    ::
    
        from lxml.etree import HTML as LXHTML
        from lxml.etree import XML as LXML
        from nvhtml import txt
        from nvhtml import lvsrch
        from nvhtml import fs
        from nvhtml import engine
        from xdict.jprint import pdir,pobj
    
    
'''


import copy
import lxml
import lxml.sax
import lxml.etree as lxe
import elist.elist as elel
from xml.sax.handler import ContentHandler
import html
import re
from nvhtml import utils
from efdir import fs
from lxml.etree import HTML as LXHTML





def pathlist(node):
    '''
        | Get a list of tags ,the tags-path  of a lxml.etree._Element
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return list: 
            list-of-tags
        
        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            node = engine.xpath_levels(root,"//a",5,6)[0]
            pl = engine.pathlist(node)
            pl
        
    '''
    pl = [each.tag for each in node.iterancestors()]
    pl.reverse()
    tag = node.tag
    if(isinstance(tag,str)):
        pass
    else:
        tag = "<comment>"
    pl.append(tag)
    return(pl)

def between_levels_cond_func(ele,start,end):
    '''
        | To check if the pathlist-lngth of  a lxml.etree._Element is between start and end
        
        :param  lxml.etree._Element ele: 
            lxml-etree-element
        :param  int start: 
            the-start-boundary(include)
        :param  int end: 
            the-end-boundary(not include)\n
        :return bool: 
            if lngth-of-pl in range(start,end), return True,\n
            else return False
            
        ::
        
            engine.pathlist(node)
            engine.between_levels_cond_func(node, 3, 6)
            engine.between_levels_cond_func(node, 7, 9)
            
    '''
    pl = pathlist(ele)
    lv = pl.__len__() - 1
    return((lv>=start)&(lv<end))

def xpath(root,xp,*args):
    '''
        | Use xpath to get lxml.etree._Elements 
        
        :param  lxml.etree._Element root: 
            lxml-etree-root-element
        :param  str xp: 
            xpath-string
        :param \*args:
            list-of-index
        :return list-or-tuple-or-lxml.etree._Element:
            if the lngth of args == 0, return list-of-all-elements\n
            elif the lngth of args == 1, return lxml.etree._Element\n
            else return tuple-of-selected-lxml.etree._Element
        
        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            eles = engine.xpath(root,"//a")
            ele =  engine.xpath(root,"//a",0)
            ele1,ele2,ele3 = engine.xpath(root,"//a",1,2,3)
        
    '''
    all = root.xpath(xp)
    args = list(args)
    if(args.__len__() ==0):
        return(all)
    if(args.__len__() ==1):
        return(all[args[0]])
    else:
        return(tuple(elel.select_seqs(all,args)))

def xpath_levels(root,xp,*args,**kwargs):
    '''
        | Use xpath to get lxml.etree._Elements, whose depth between range(start,end)
        
        :param  lxml.etree._Element root: 
            lxml-etree-root-element
        :param  str xp: 
            xpath-string
        :param \*args:
            refer to exampls below
        :param \*\*kwargs:
            refer to exampls below
        :return list:
            list-of-lxml.etree._Element

        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            #eles = engine.xpath_levels(root,"//a",start,end)
            eles = engine.xpath_levels(root,"//a",5,6)
            #eles = engine.xpath_levels(root,"//a",start)
            eles = engine.xpath_levels(root,"//a",5)
            #eles = engine.xpath_levels(root,"//a",start=0,end=ei)
            eles = engine.xpath_levels(root,"//a",end=8)
            #eles = engine.xpath_levels(root,"//a",start=7,end=last)
            eles = engine.xpath_levels(root,"//a",start=7)
            #eles = engine.xpath_levels(root,"//a",start=si,end=ei)
            eles = engine.xpath_levels(root,"//a",start=7,end=9)
        
    '''
    start,end,rel = utils.arguments_levels(*args,**kwargs)
    all = root.xpath(xp)
    selected = elel.cond_select_values_all(all,cond_func = between_levels_cond_func,cond_func_args=[start,end])
    return(selected)

def plget(root,*args,**kwargs):
    '''
        | Get lxml.etree._Elements using pathlist
        
        :param  lxml.etree._Element root: 
            lxml-etree-root-element
        :param \*args:
            refer to exampls below
        :param \*\*kwargs:
            refer to exampls below
        :return list:
            tuple-of-lxml.etree._Elements
            or list-of-lxml.etree._Elements
            or lxml.etree._Element
        
        ::
        
            engine.plget(root,"a")
            #()
            engine.plget(root,"a",strict=False)
            engine.plget(root,['html', 'body', 'div', 'div'])
            engine.plget(root,'html', 'body', 'div', 'div')
            #[<Element div at 0x21602c68dc8>, <Element div at 0x21602a9f748>, <Element div at 0x21602c68e48>, <Element div at 0x21602c68f48>, <Element div at 0x21602c68ec8>, <Element div at 0x21602c68f08>]
            engine.plget(root,'html', 'body', 'div', 'div',whiches=[2,3,4])
            #(<Element div at 0x21602c68e48>, <Element div at 0x21602c68f48>, <Element div at 0x21602c68ec8>)
            engine.plget(root,'html', 'body', 'div', 'div',whiches=3)
            #<Element div at 0x21602c68f48>
    '''
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
    return(xpath(root,xp,*whiches))

def source(node,codec='utf-8'):
    '''
        | Get the source-txt  of a lxml.etree._Element
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :param  str codec: 
            by default,codec='utf-8'
        :return str: 
            source-txt of lxml.etree._Element
        
        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            ele1,ele2,ele3 = engine.xpath(root,"//a",1,2,3)
            print(engine.source(ele1))
            print(engine.source(ele2))
        
    '''
    if(node == None):
        return(None)
    else:
        rslt = lxe.tostring(node).decode(codec)
        rslt = html.unescape(rslt)
        return(rslt)

def txtize(nodes):
    '''
        | Return a list of source-txts of lxml.etree._Elements
    
        :param  lxml.etree._Element nodes: 
            a list of lxml-etree-elements
        :return str: 
            a list of source-txts of lxml.etree._Elements
        
        ::
        
            from nvhtml import utils
            eles = list(engine.xpath(root,"//a",1,2,3))
            txts = engine.txtize(eles)
            utils.parr(txts)
        
    '''
    txts = elel.mapv(nodes,source,[])
    return(txts)

def text_intag(node):
    '''
        | Get the source-txt  between start-tag and end-tag,
        | but not include descedants text(NOT itertext),
        | node.text + each son.tail
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return str: 
            text-intag
            see the examples below
            
        ::
        
            html_str =  """<div>
                div-text
                <p>
                    p-text
                </p>
                p-tail-in-div-closure
            </div>"""
            
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//div",0)
            print(engine.text_intag(ele))
            #>>> print(engine.text_intag(ele))
            #
            #    div-text
            #
            #    p-tail-in-div-closure
            #
            #>>>

    '''
    txts = node.xpath("./text()")
    s = elel.join(txts,"")
    return(s)

def is_leaf(node):
    '''
        | Is leaf-node or not(have children)
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return bool: 
            if leaf, return True
    '''
    eles = node.getchildren()
    cond = (eles.__len__() == 0)
    return(cond)

def parent(node):
    '''
        | Get parent-node
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return lxml.etree._Element: 
            parent-node
    '''
    return(node.getparent())



def grand_parent(node):
    '''
        | Get grand-parent-node
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return lxml.etree._Element: 
            grand-parent-node
    '''
    return(node.getparent().getparent())

def ancestor(node,which,pl=None):
    '''
        | Get ancestor
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :param  int which: 
            which ancestor, parent 1,grand_parent 2.....
        :return lxml.etree._Element: 
            ancestor-node
    '''
    if(pl == None):
        pl = pathlist(node)
    else:
        pass
    lngth = pl.__len__()
    if(which > lngth - 1):
        which = lngth - 1
    elif(which < 0):
        which = 0
    else:
        pass
    while(which>0):
        node = node.getparent()
        which = which - 1
    return(node)

def ancestors(node,*args,**kwargs):
    '''
        | Get ancestor
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :param  \*args: 
            see examples below
        :param  \*\*kwargs: 
            see examples below
        :return list: 
            ancestor-nodes
        
        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//a",0)
            eles = engine.ancestors(ele)
            # [<Element div at 0x21ec4c5d108>, <Element div at 0x21ec4c5d208>, <Element body at 0x21ec4c5d188>, <Element html at 0x21ec4ebe8c8>]
            eles = engine.ancestor(ele,1)
            # <Element div at 0x21ec4c5d108>
            eles = engine.ancestors(ele,2,3)
            # [<Element div at 0x21ec4c5d208>, <Element body at 0x21ec4c5d188>]
            eles = engine.ancestors(ele,start=2)
            # [<Element div at 0x21ec4c5d208>, <Element body at 0x21ec4c5d188>, <Element html at 0x21ec4ebe8c8>]
            eles = engine.ancestors(ele,end=2)
            # [<Element div at 0x21ec4c5d108>]
            eles = engine.ancestors(ele,start=2,end=4)
            # [<Element div at 0x21ec4c5d208>, <Element body at 0x21ec4c5d188>]
        
    '''
    def map_func(which,node,pl):
        return(ancestor(node,which,pl))
    pl = pathlist(node)
    lngth = pl.__len__()
    if('start' in kwargs):
        pass
    else:
        kwargs['start'] = 1
    whiches = utils.arguments_whiches(lngth,*args,**kwargs)
    whiches = elel.cond_remove_all(whiches, cond_func = lambda ele:(ele>lngth))
    ances = elel.mapv(whiches,map_func,[node,pl])
    return(ances)

def children(node,*args,**kwargs):
    '''
        | Get children
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :param  \*args: 
            see examples below
        :param  \*\*kwargs: 
            see examples below
        :return list: 
            list-of-child-nodes
        
        ::

            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//div",0)
            childs = engine.children(ele)
            childs
            # [<Element div at 0x1a8609755c8>, <Element div at 0x1a860973988>, <Element div at 0x1a860973b48>, <Element div at 0x1a860973a88>, <!-- maincontent end -->, <Element div at 0x1a860973b08>, <Element div at 0x1a860973908>]
            engine.children(ele,0)
            # [<Element div at 0x1a8609755c8>]
            engine.children(ele,4)
            # [<!-- maincontent end -->]
            engine.children(ele,6)
            # [<Element div at 0x1a860973908>]
            engine.children(ele,1,3,5)
            # [<Element div at 0x1a860973988>, <Element div at 0x1a860973a88>, <Element div at 0x1a860973b08>]
            engine.children(ele,[1,3,5])
            # [<Element div at 0x1a860973988>, <Element div at 0x1a860973a88>, <Element div at 0x1a860973b08>]
            engine.children(ele,start=1,end=4)
            # [<Element div at 0x1a860973988>, <Element div at 0x1a860973b48>, <Element div at 0x1a860973a88>]

    '''
    childs = node.getchildren()
    lngth = childs.__len__()
    whiches = utils.arguments_whiches(lngth,*args,**kwargs)
    whiches = elel.cond_remove_all(whiches, cond_func = lambda ele:(ele>lngth))
    childs = elel.select_seqs(childs,whiches)
    return(childs)

def child(node,which):
    '''
        | Get child
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :param  int which: 
            which child
        :return lxml.etree._Element: 
            child-node
        
        ::

            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//div",0)
            engine.child(ele,2)
    '''
    try:
        chld = children(node,which)[0]
    except:
        chld = None
    else:
        pass
    return(chld)

def sibseq(node):
    '''
        | Get the sequence-number of siblings(share the same parent)
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return int: 
            the sequence-number of siblings
        
        ::

            html_str = """
            <html>
                <head>
                </head>
                <body>
                    <div-out-1>
                        <div id="0">b0</div>
                        <div id="1">b1</div>
                        <div id="2">b2</div>
                        <div id="3">b3</div>
                    </div-out-1>
                    <div-out-2>
                        <li id="0">l0</li>
                        <li id="1">l1</li>
                        <li id="2">l2</li>
                        <li id="3">l3</li>
                    </div-out-2>
                </body>
            </html>
            """
            
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-1/div",2)
            ele.text
            # 'b2'
            engine.sibseq(ele)
            # 2
        
    '''
    p = node.getparent()
    if(p == None):
        return(0)
    else:
        childs = p.getchildren()
        total = childs.__len__()
        for i in range(0,total):
            if(node == childs[i]):
                curr_seq = i
                return(curr_seq)
            else:
                pass

def siblings(node,*args,**kwargs):
    '''
        | Get siblings(share the same parent)
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :param  \*args: 
            see examples below
        :param  \*\*kwargs: 
            see examples below
        :return list: 
            list-of-sibling-nodes
        
        ::

            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-1/div",2)
            sibs = engine.siblings(ele)
            sibs
            #[<Element div at 0x1d3f56f2808>, <Element div at 0x1d3f56f2848>, <Element div at 0x1d3f56f0308>, <Element div at 0x1d3f56f2888>]
            engine.siblings(ele,0)
            #[<Element div at 0x1d3f56f2808>]
            engine.siblings(ele,3)
            #[<Element div at 0x1d3f56f2888>]
            engine.siblings(ele,1,2)
            #[<Element div at 0x1d3f56f2848>, <Element div at 0x1d3f56f0308>]
            engine.siblings(ele,[1,2,3])
            #[<Element div at 0x1d3f56f2848>, <Element div at 0x1d3f56f0308>, <Element div at 0x1d3f56f2888>]
            engine.siblings(ele,start=2,end=3)
            #[<Element div at 0x1d3f56f0308>]
        
    '''
    p = node.getparent()
    if(p == None):
        return([node])
    else:
        childs = children(p,*args,**kwargs)
    return(childs)

def samepl_siblings(node,*args,**kwargs):
    '''
        | Get siblings(share the same parent) which have the same pathlist 
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return list: 
            list-of-child-nodes
        
        ::
        
            html_str = """
            <html>
                <head>
                </head>
                <body>
                    <div-out-1>
                        <divx id="0">b0</divx>
                        <divy id="1">b1</divy>
                        <divx id="2">b2</divx>
                        <divy id="3">b3</divy>
                    </div-out-1>
                    <div-out-2>
                        <li id="0">l0</li>
                        <li id="1">l1</li>
                        <li id="2">l2</li>
                        <li id="3">l3</li>
                    </div-out-2>
                </body>
            </html>
            """
            
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-1/divx",0)
            eles = engine.samepl_siblings(ele)
            eles
            # [<Element divx at 0x251425b9cc8>, <Element divx at 0x251425bf888>]
            engine.pathlist(eles[0])
            # engine.pathlist(eles[0])
            engine.pathlist(eles[1])
            # engine.pathlist(eles[1])
    '''
    pl = pathlist(node)
    sibs = siblings(node,*args,**kwargs)
    sibs = elel.cond_select_values_all(sibs,cond_func=lambda node,pl:(pathlist(node) == pl),cond_func_args=[pl])
    return(sibs)

def samepl_sibseq(node,*args,**kwargs):
    '''
        | Get the sequence-number of siblings which have the same pathlist 
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return int: 
            the sequence-number of siblings which have the same pathlist 
        
        ::
            
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-1/divx",1)
            engine.sibseq(ele)
            # 2
            engine.samepl_sibseq(ele)
            # 1

    '''
    c = 0
    pl = pathlist(node)
    p = node.getparent()
    if(p == None):
        c = 1
        return(0)
    else:
        childs = p.getchildren()
        total = childs.__len__()
        for i in range(0,total):
            if(pathlist(childs[i]) == pl):
                c = c + 1
            else:
                pass
            if(node == childs[i]):
                return(c-1)
            else:
                pass

def lsib(node):
    '''
        | Get the left sibling 
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return lxml.etree._Element: 
            left-sibling
        
        ::
            
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-1/divx",1)
            engine.lsib(ele)
            # <divy id="1">b1</divy>
            ele = engine.xpath(root,"//body/div-out-1/divx",0)
            # <divx id="0">b0</divx>
            engine.lsib(ele)
            # None beacuse  <divx id="0">b0</divx>  is the left-most child of <div-out-1>
            
    '''
    seq = sibseq(node)
    sibs = siblings(node)
    lngth = sibs.__len__()
    lseq = seq - 1
    if(lseq < 0):
        return(None)
    elif(lseq>(lngth -1)):
        return(None)
    else:
        return(sibs[lseq])

def rsib(node):
    '''
        | Get the right sibling 
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return lxml.etree._Element: 
            right-sibling
        
        ::
            
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-1/divy",1)
            # <divy id="3">b3</divy>
            engine.rsib(ele)
            # None beacuse  <divy id="3">b3</divy>  is the right-most child of <div-out-1>
            ele = engine.xpath(root,"//body/div-out-1/divy",0)
            # <divy id="1">b1</divy>
            print(engine.source(engine.rsib(ele)))
            # <divx id="2">b2</divx>
            
    '''
    seq = sibseq(node)
    sibs = siblings(node)
    lngth = sibs.__len__()
    rseq = seq + 1
    if(rseq < 0):
        return(None)
    elif(rseq>(lngth -1)):
        return(None)
    else:
        return(sibs[rseq])

def preceding_sibs(node):
    '''
        | Get the left-side siblings 
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return list: 
            siblings-before-node
    '''
    curr_seq = sibseq(node)
    sibs = siblings(node)
    return(sibs[:curr_seq])

def following_sibs(node):
    '''
        | Get the right-side siblings 
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return list: 
            siblings-after-node
    '''
    curr_seq = sibseq(node)
    sibs = siblings(node)
    return(sibs[(curr_seq+1):])

def lcin(node):
    '''
        | Get the left cousin (adjancent to the left,but have different parent)
        
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return lxml.etree._Element: 
            left-cousin
        
        ::
            
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-2/li",0)
            # <li id="0">l0</li>
            print(engine.source(engine.lcin(ele)))
            #<divy id="3">b3</divy>
            
    '''
    seq = sibseq(node)
    if(seq == 0):
        p = parent(node)
        if(p == None):
            return(None)
        else:
            plsib = lsib(p)
            if(plsib == None):
                return(None)
            else:
                plsibchilds = children(plsib)
                if(plsibchilds == None):
                    return(None)
                else:
                    return(plsibchilds[-1])
    else:
        return(None)

def rcin(node):
    '''
        | Get the right cousin (adjancent to the right,but have different parent)
        
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return lxml.etree._Element: 
            right-cousin
        
        ::
            
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-1/divy",1)
            # <divy id="3">b3</divy>
            print(engine.source(engine.rcin(ele)))
            # <li id="0">l0</li>
            
    '''
    seq = sibseq(node)
    sibs = siblings(node)
    lngth = sibs.__len__()
    if(seq == (lngth-1)):
        p = parent(node)
        if(p == None):
            return(None)
        else:
            prsib = rsib(p)
            if(prsib == None):
                return(None)
            else:
                prsibchilds = children(prsib)
                if(prsibchilds == None):
                    return(None)
                else:
                    return(prsibchilds[0])
    else:
        return(None)


def rootnode(node):
    '''
        | Get all the lxml.etree._Elements in the same layer(have the same pathlist lngth)
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return lxml.etree._Element: 
            root-node
    '''
    p = node.getparent()
    if(p == None):
        return(node)
    else:
        while(p!= None):
            prev = p
            p = p.getparent()
    return(prev)

def layer(node,**kwargs):
    '''
        | Get all the lxml.etree._Elements in the same layer(have the same pathlist lngth)
        
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return list: 
            the list of lxml.etree._Elements in the same layer
        
        ::
            
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-1/divy",1)
            utils.parr(engine.layer(ele))
            <Element divx at 0x2a541a5bfc8>
            <Element divy at 0x2a541a4a1c8>
            <Element divx at 0x2a541a4a208>
            <Element divy at 0x2a541a4a248>
            <Element li at 0x2a541a58848>
            <Element li at 0x2a541a4a3c8>
            <Element li at 0x2a541a4a408>
            <Element li at 0x2a541a4a448>
            
    '''
    root = rootnode(node)
    pl = pathlist(node)
    lngth = pl.__len__()
    kwargs['handler'] = layer_wfs_handler
    kwargs['until'] = lngth
    wfs = WFS(root,**kwargs)
    lyr = wfs.mat[lngth-1]
    lyr = elel.mapv(lyr,lambda ele:ele['node'],[])
    return(lyr)
    

def depth(node):
    '''
        | Get the depth of lxml.etree._Element(depth = the-lngth-of-pathlist - 1)
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return int: 
            the depth of lxml.etree._Element
        
    '''
    pl = pathlist(node)
    return(pl.__len__()-1)

def breadth(node):
    '''
        | Get the breadth of lxml.etree._Element in the layer
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return int: 
            the breadth of lxml.etree._Element
        
        ::
        
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-2/li",0)
            engine.breadth(ele)
            #4
            
    '''
    if(node == None):
        return(None)
    else:
        pass
    #lyr = layer(node)
    #for i in range(lyr.__len__()):
    #    if(lyr[i] == node):
    #        return(i)
    #    else:
    #        pass
    p = parent(node)
    breadth = p.index(node)
    return(breadth)

def parent_breadth(node):
    p = parent(node)
    return(breadth(p))


def loc(node):
    '''
        | Get the location(breadth,depth) of lxml.etree._Element in the desc-matrix
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return tuple: 
            (breadth,depth)
        
        ::
        
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-2/li",0)
            engine.loc(ele)
            #(4,3)
            
    '''
    return((breadth(node),depth(node)))

def samepl_breadth(node):
    '''
        | Get the sequence-number of lxml.etree._Element in the elements having the same pathlist (whole layer ,NOT just the siblings)
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return int: 
            the breadth in the-whole-same-pathlist-elements
        
        ::
        
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body/div-out-2/divx",0)
            engine.sampl_breadth(ele)
            # 2
    '''
    pl = pathlist(node)
    lyr = layer(node)
    c = 0
    for i in range(len(lyr)):
        ele = lyr[i]
        ele_pl = pathlist(ele)
        if(ele_pl == pl):
            c = c + 1
        else:
            pass
        if(node == ele):
            return(c-1)
        else:
            pass

def descendants(node,*args,**kwargs):
    '''
        | Get Descendants
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :param  \*args: 
            see examples below
        :param  \*\*kwargs: 
            see examples below
        :return list: 
            list-of-decedants-nodes
        
        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            engine.descendants(root).__len__()
            # 867
            engine.descendants(root,1,2)
            # [<Element head at 0x2ec39e02f08>, <Element body at 0x2ec39e12148>]
            engine.descendants(root,0,1)
            # [<Element html at 0x2ec3a126608>]
            eles = engine.descendants(root,5,7)
            # start = 5 ,end =7, to get the nodes whose depth between 5 and 7 
            engine.pathlist(eles[0])
            # ['html', 'body', 'div', 'div', 'div', 'script']
            engine.pathlist(eles[100])
            # ['html', 'body', 'div', 'div', 'div', 'ul', 'li']

    '''
    
    start,end,rel = utils.arguments_levels(*args,**kwargs)
    unhandled = [node]
    next_unhandled = []
    dscdnts = []
    while(unhandled.__len__()>0):
        for i in range(0,unhandled.__len__()):
            each_node = unhandled[i]
            childs = each_node.getchildren()
            if(childs.__len__() == 0):
                dscdnts.append(each_node)
            else:
                dscdnts.append(each_node)
                next_unhandled = next_unhandled + childs
        unhandled = next_unhandled
        next_unhandled = []
    dscdnts = elel.cond_select_values_all(dscdnts,cond_func = between_levels_cond_func,cond_func_args=[start,end])
    return(dscdnts)

#
def extract_pls(node,dscdnts,rel="False"):
    pls = elel.mapv(dscdnts,pathlist,[])
    if(rel==True):
        lngth = pathlist(node).__len__()
        pls = elel.mapv(pls,lambda rslt:rslt[lngth:],[])
    else:
        pass
    return(pls)

def descendants_pls(node,*args,**kwargs):
    '''
        | Get Descendant pathlists
        
        :param  lxml.etree._Element node: 
            lxml-etree-element
        :param  \*args: 
            see examples below
        :param  \*\*kwargs: 
            see examples below
        :return list: 
            list-of-decedants-pathlists
        
        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            ele = engine.xpath(root,"//body",0)
            engine.descendants_pls(ele).__len__()
            # 852
            pls = engine.descendants_pls(ele,5,7)
            # start = 5 ,end =7, to get the nodes whose depth between 5 and 7 
            pls[0]
            # ['html', 'body', 'div', 'div', 'div', 'script']
            pls[100]
            # ['html', 'body', 'div', 'div', 'div', 'ul', 'li']
            engine.pathlist(root)
            # ['html']
            engine.pathlist(ele)
            # ['html', 'body']
            pls = engine.descendants_pls(ele,5,7,rel=True)
            # relative pathlist
            pls[0]
            # ['div', 'div', 'div', 'script']
            pls[100]
            # ['div', 'div', 'div', 'ul', 'li']

    '''
    start,end,rel = utils.arguments_levels(*args,**kwargs)
    dscdnts = descendants(node,*args,**kwargs)
    return(extract_pls(node,dscdnts,rel))

def leaf_descendants(node,*args,**kwargs):
    '''
        | Same as descendants, but only leaf-decendants
    '''
    dscdnts = descendants(node,*args,**kwargs)
    dscdnts = elel.cond_select_values_all(dscdnts,cond_func = is_leaf)
    return(dscdnts)

def leaf_descendants_pls(node,*args,**kwargs):
    '''
        | Same as descendants_pls, but only leaf-decendants
    '''
    start,end,rel = utils.arguments_levels(*args,**kwargs)
    dscdnts = leaf_descendants(node,*args,**kwargs)
    return(extract_pls(node,dscdnts,rel))

def nonleaf_descendants(node,*args,**kwargs):
    '''
        | Same as descendants, but only nonleaf-decendants
    '''
    dscdnts = descendants(node,*args,**kwargs)
    dscdnts = elel.cond_select_values_all(dscdnts,cond_func = lambda node:not(is_leaf(node)))
    return(dscdnts)

def nonleaf_descendants_pls(node,*args,**kwargs):
    '''
        | Same as descendants_pls, but only nonleaf-decendants
    '''
    start,end,rel = utils.arguments_levels(*args,**kwargs)
    dscdnts = nonleaf_descendants(node,*args,**kwargs)
    return(extract_pls(node,dscdnts,rel))

def disconnect(node):
    '''
        | Disconnect 

        :param  lxml.etree._Element node: 
            lxml-etree-element
        :return lxml.etree._Element: 
            the disconnected node
        
        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            # <Element html at 0x2ec3a13ee08>
            ele = engine.xpath(root,"//body",0)
            # <Element body at 0x2ec3a14da08>
            ele.getparent()
            # <Element html at 0x2ec3a13ee08>
            engine.disconnect(ele)
            # <Element body at 0x2ec3a14da08>
            ele.getparent()
            # None
            root.getchildren()
            # [<Element head at 0x2ec39e1f5c8>]
        
    '''
    p = node.getparent()
    if(p == None):
        pass
    else:
        p.remove(node)
    return(node)

#dom tree

def layer_wfs_handler(each_node,pls,breadth,pbreadth,root,p_mkdir_pth):
    pl = pathlist(each_node)
    which = pls.count(pl)
    pls.append(pl)
    d = {}
    d['node'] = each_node
    return(d)



def default_wfs_handler(each_node,pls,breadth,pbreadth,root,p_mkdir_pth):
    pl = pathlist(each_node)
    which = pls.count(pl)
    pls.append(pl)
    d = {}
    d['pl'] = pl
    d['breadth'] = breadth
    d['depth'] = len(pl) - 1
    d['pbreadth'] = pbreadth
    d['samepl_sibseq'] = samepl_sibseq(each_node)
    d['samepl_breadth'] = which
    ####
    #d['samepl_siblings_total'] = samepl_siblings(each_node).__len__()
    #d['samepl_total'] = None
    ####
    #d['tag'] = str(each_node.tag)
    d['tag'] = str(pl[-1])
    d['sibseq'] = sibseq(each_node)
    d['attrib'] = dict(each_node.attrib)
    d['text'] = each_node.text
    d['tail'] = each_node.tail
    d['text_intag'] = text_intag(each_node)
    #d['node'] = each_node
    d['mkdir_pth'] = p_mkdir_pth + "/" +d['tag'] + "."+str(d['breadth'])
    #if(drop_comment & (d['tag'] == "<comment>")):
    #    return(None)
    #else:
    return(d)

def init_cls_wfs_arguments(**kwargs):
    if("until" in kwargs):
        until = kwargs["until"]
    else:
        until = 2*32
    if("handler" in kwargs):
        handler = kwargs["handler"]
    else:
        handler = default_wfs_handler
    if("yield_d" in kwargs):
        yield_d = kwargs['yield_d']
    else:
        yield_d = False
    if("yield_currlv" in kwargs):
        yield_currlv = kwargs['yield_currlv']
    else:
        yield_currlv = False
    if("yield_curr_next_unhandled" in kwargs):
        yield_curr_next_unhandled = kwargs['yield_curr_next_unhandled']
    else:
        yield_curr_next_unhandled = False
    if("drop_comment" in kwargs):
        drop_comment = kwargs['drop_comment']
    else:
        drop_comment = False
    if("drop_cdata" in kwargs):
        drop_cdata = kwargs['drop_cdata']
    else:
        drop_cdata = False
    return((handler,until,yield_d,yield_currlv,yield_curr_next_unhandled,drop_comment,drop_cdata))


class WFS():
    '''
        | Get description-matrix of a lxml.etree._Element root
          
        
        :param  lxml.etree._Element root: 
            lxml-etree-element
        :param  \*args: 
            see examples below
        :param  function kwargs\['handler'\]: 
            default:default_wfs_handler(each_node,breadth)
        :param  int kwargs\['until'\]: 
            until which-layer(before this layer)
            default:traverse-all-levels
        :return obj:
            see examples below
        
        ::
        
            the default_wfs_handler
                def default_wfs_handler(each_node,pls,breadth):
                    pl = pathlist(each_node)
                    which = pls.count(pl)
                    pls.append(pl)
                    d = {}
                    d['pl'] = pl
                    d['samepl_sibseq'] = samepl_sibseq(each_node)
                    d['samepl_breadth'] = which
                    d['tag'] = str(each_node.tag)
                    d['sibseq'] = sibseq(each_node)
                    d['attrib'] = dict(each_node.attrib)
                    d['text'] = each_node.text
                    d['tail'] = each_node.tail
                    d['text_intag'] = text_intag(each_node)
                    d['node'] = each_node
                    return(d)
        
        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            wfs = engine.WFS(root)
            wfs.depth
            #8
        
        ::
        
            pobj(wfs.mat[3][1])
            
            {
             'pl':
                   [
                    'html',
                    'body',
                    'div',
                    'div'
                   ],
             'samepl_sibseq': 1,
             'samepl_breadth': 1,
             'tag': 'div',
             'sibseq': 1,
             'attrib':
                       {
                        'id': 'navfirst'
                       },
             'text': '\\r\\n',
             'tail': '\\r\\n\\r\\n',
             'text_intag': '\\r\\n\\r\\n',
             'node': <Elementdivat0x24135ef9a88>
            }
            

    '''
    def __init__(self,root,**kwargs):
        handler,until,yield_d,yield_currlv,yield_curr_next_unhandled,drop_comment,drop_cdata = init_cls_wfs_arguments(**kwargs)
        ######
        if(drop_comment):
            lxml.etree.strip_tags(root,lxml.etree.Comment)
        else:
            pass
        if(drop_cdata):
            lxml.etree.strip_tags(root,lxml.etree.CDATA)
        else:
            pass
        ######
        self.root = root
        self.mat = []
        unhandled = [{'node':root,'pbreadth':None,'p_mkdir_pth':""}]
        next_unhandled = []
        self.depth = -1
        while(unhandled.__len__()>0):
            if(self.depth<until):
                ########
                #yield_unhandled and (yield unhandled)
                ########
                curr_level = []
                self.mat.append(curr_level)
                pls = []
                for i in range(0,unhandled.__len__()):
                    each_node = unhandled[i]['node']
                    pbreadth = unhandled[i]['pbreadth'] 
                    p_mkdir_pth = unhandled[i]['p_mkdir_pth']
                    d = handler(each_node,pls,i,pbreadth,root,p_mkdir_pth)
                    #if(d != None):
                    cp_mkdir_pth = d['mkdir_pth']
                        ######################################
                    child_nodes = each_node.getchildren()
                    childs = elel.mapv(child_nodes,lambda nd:{'node':nd,'pbreadth':i,"p_mkdir_pth":cp_mkdir_pth})
                        ###########################
                        #yield_d and (yield (d,i))
                        #######
                    curr_level.append(d)
                        #######
                    #else:
                    #    childs = []
                    #yield_currlv and (yield (curr_level,i))
                    #######
                    if(childs.__len__() == 0):
                        pass
                    else:
                        next_unhandled = next_unhandled + childs
                    ########
                    #yield_curr_next_unhandled and (yield (next_unhandled,i))
                    #######
                #####
                #for i in range(0,curr_level.__len__()):
                #    d = curr_level[i]
                #    d['samepl_total'] = pls.count(d['pl'])
                #####
                unhandled = next_unhandled
                next_unhandled = []
                self.depth = self.depth + 1
            else:
                break


def wfs_traverse(root,**kwargs):
    '''
        | Same as class WFS ,just return the object(include .mat and .root)
        | using default_wfs_handler
    '''
    rslt = WFS(root,**kwargs)
    return(rslt)

def wfspls(root,**kwargs):
    '''
        | pathlist-sequence of  width-first-traverse  
          
        
        :param  lxml.etree._Element root: 
            lxml-etree-element
        :return list:
            list of pathlists  in width-first-traverse-sequence
    
    ::
    
        html_str = fs.rfile("./test.html")
        root = LXHTML(html_str)
        pls = engine.wfspls(root)
        utils.parr(pls[:10])
        >>>
        ['html']
        ['html', 'head']
        ['html', 'body']
        ['html', 'head', <cyfunction Comment at 0x0000024135C12550>]
        ['html', 'head', 'script']
        ['html', 'head', 'script']
        ['html', 'head', 'meta']
        ['html', 'head', 'meta']
        ['html', 'head', 'meta']
        ['html', 'head', 'link']
        >>>
        utils.parr(pls[-10:])
        ['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'td', 'a']
        ['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'td', 'a']
        ['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'td', 'a']
        ['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'td', 'a']
        ['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'td', 'span']
        ['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'td', 'a']
        ['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'td', 'a']
        ['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'td', 'a']
        ['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'td', 'a']
        ['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'td', 'span']
        
    '''
    wfs = wfs_traverse(root,**kwargs)
    m = wfs.mat
    pls = udlr_wfspls(m)
    return(pls)


def udlr_wfspls(m):
    pls = []
    for i in range(m.__len__()):
        desc_lyr = m[i]
        for j in range(desc_lyr.__len__()):
            desc = desc_lyr[j]
            #pl = copy.copy(desc['pl'])
            pl = elel.fcp(desc['pl'])
            pls.append(pl)
    return(pls)


def udrl_wfspls(m):
    pls = []
    for i in range(m.__len__()):
        desc_lyr = m[i]
        for j in range(desc_lyr.__len__()-1,-1,-1):
            desc = desc_lyr[j]
            #pl = copy.copy(desc['pl'])
            pl = elel.fcp(desc['pl'])
            pls.append(pl)
    return(pls)


def dulr_wfspls(m):
    pls = []
    for i in range(m.__len__()-1,-1,-1):
        desc_lyr = m[i]
        for j in range(desc_lyr.__len__()):
            desc = desc_lyr[j]
            #pl = copy.copy(desc['pl'])
            pl = elel.fcp(desc['pl'])
            pls.append(pl)
    return(pls)


def durl_wfspls(m):
    pls = []
    for i in range(m.__len__()-1,-1,-1):
        desc_lyr = m[i]
        for j in range(desc_lyr.__len__(),-1,-1):
            desc = desc_lyr[j]
            #pl = copy.copy(desc['pl'])
            pl = elel.fcp(desc['pl'])
            pls.append(pl)
    return(pls)





def loc2node(root,*args,**kwargs):
    '''
        | Get node Via breadth,depth

        :param  \*args: 
            breadth,depth or (depth,breadth)
        :return lxml.etree._Element:
            not at location (depth,breadth)
        
        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            node = engine.loc2node(root,5,6)
            node
            # <Element li at 0x1c1502acd48>
            engine.depth(node)
            # 5
            engine.breadth(node)
            # 6
    '''
    args = list(args)
    if(isinstance(args[0],tuple)):
        x,y = args[0]
    else:
        x = args[0]
        y = args[1]
    handler = WFS(root,**kwargs)
    mat = handler.mat
    return(mat[x][y]['node'])


########################################################
#fill attr

def init_attr(mat,attr,value):
    lngth = len(mat)
    for i in range(lngth):
        layer = mat[i]
        for j in range(layer.__len__()):
            ele = layer[j]
            ele[attr] = copy.deepcopy(value)
    return(mat)

##

def fill_children_attr(mat):
    depth = len(mat)
    for i in range(depth-1,0,-1):
        layer = mat[i]
        breadth = len(layer)
        for j in range(breadth):
            ele = layer[j]
            pbreadth = ele['pbreadth']
            pchildren = mat[i-1][pbreadth]['children']
            pchildren.append((i,j))
    return(mat)

########################################################

#sax

class EDFS_SAX(ContentHandler):
    '''
        | Get sax-style deep-first-traverse  of a lxml.etree._Element root
          
        :param  bool kwargs['attrib_pl']: 
            return full-info attrib-path-list corresponding to path-list
        :return obj:
            return a obj for lxml.sax.saxify
        
        ::
            
            if using xml-mode
                from io import StringIO
                f = StringIO(s)
                root = lxe.parse(f)
            
        ::
        
            import lxml.sax
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            edfs = engine.EDFS_SAX()
            lxml.sax.saxify(root, edfs)
            utils.parr(edfs.pls[:5])
            >>>
            ['html', 'head', 'script']
            ['html', 'head', 'script']
            ['html', 'head', 'meta']
            ['html', 'head', 'meta']
            ['html', 'head', 'meta']
            utils.parr(edfs.pls[-10:])
            ['html', 'body', 'div', 'div', 'div', 'script']
            ['html', 'body', 'div', 'div', 'div']
            ['html', 'body', 'div', 'div']
            ['html', 'body', 'div', 'div', 'p']
            ['html', 'body', 'div', 'div', 'p', 'a']
            ['html', 'body', 'div', 'div', 'p']
            ['html', 'body', 'div', 'div']
            ['html', 'body', 'div']
            ['html', 'body']
            ['html']
            >>>
            utils.parr(edfs.datas[-5:])
            [(['html', 'body', 'div', 'div', 'p'], '\\r\\n使用条款和隐私条款。版权所有，保留一切权利。\\r\\n赞助商：'), (['html', 'body', 'div', 'div', 'p'], '。\\r\\n蒙ICP备06004630号\\r\\n')]
            [(['html', 'body', 'div', 'div'], '\\r\\n'), (['html', 'body', 'div', 'div'], '\\r\\n\\r\\n'), (['html', 'body', 'div', 'div'], '\\r\\n')]
            [(['html', 'body', 'div'], '\\r\\n\\r\\n'), (['html', 'body', 'div'], '\\r\\n\\r\\n'), (['html', 'body', 'div'], '\\r\\n\\r\\n'), (['html', 'body', 'div'], '\\r\\n\\r\\n'), (['html', 'body', 'div'], '\\r\\n'), (['html', 'body', 'div'], '\\r\\n\\r\\n'), (['html', 'body', 'div'], '\\r\\n\\r\\n'), (['html', 'body', 'div'], '\\r\\n\\r\\n\\r\\n')]
            [(['html', 'body'], '\\r\\n\\r\\n'), (['html', 'body'], '\\r\\n'), (['html', 'body'], '\\r\\n\\r\\n')]
            [(['html'], '\\r\\n'), (['html'], '\\r\\n\\r\\n'), (['html'], '\\r\\n\\r\\n')]
            >>>
            utils.parr(edfs.attribs[-5:])
            {'id': 'p2'}
            {'id': 'footer'}
            {'id': 'wrapper'}
            {'class': 'html'}
            {'lang': 'zh-cn'}
            >>>
            edfs = engine.EDFS_SAX(full_attrib=True)
            lxml.sax.saxify(root, edfs)
            utils.parr(edfs.attribs[-5:])
            >>>
            [('lang', 'zh-cn'), ('class', 'html'), ('id', 'wrapper'), ('id', 'footer'), ('id', 'p2')]
            [('lang', 'zh-cn'), ('class', 'html'), ('id', 'wrapper'), ('id', 'footer')]
            [('lang', 'zh-cn'), ('class', 'html'), ('id', 'wrapper')]
            [('lang', 'zh-cn'), ('class', 'html')]
            [('lang', 'zh-cn')]
            >>>
        
    '''
    @classmethod
    def attrl2tl(cls,attrl):
        tl = []
        for i in range(attrl.__len__()):
            attr = attrl[i]
            if(attr.__len__() == 0):
                tl.append(tuple([]))
            else:
                tl.append((attr[0][0][1],attr[0][1]))
        return(tl)
    @classmethod
    def attrl2dl(cls,attrl):
        dl = []
        for i in range(attrl.__len__()):
            attr = attrl[i]
            if(attr.__len__() == 0):
                dl.append({})
            else:
                d = {}
                d[attr[0][0][1]] = attr[0][1]
                dl.append(d)
        return(dl)
    def __init__(self,**kwargs):
        if("attrib_pl" in kwargs):
            self.attrib_pl = kwargs['attrib_pl']
        else:
            self.attrib_pl = False
        self.pls = []
        self.attribs = []
        self.currpl =[]
        self.currattribl = []
        self.datas = []
        self.currdatal = []
        self.texts_inseq = []
        self.tags = set({})
    def startElementNS(self, name, qname, attributes):
        self.currdatal.append(None)
        self.currpl.append(qname)
        self.currattribl.append(attributes.items())
    def endElementNS(self, ns_name, qname):
        #####
        self.tags.add(qname)
        #####
        index = elel.index_last(self.currdatal,None)
        data = copy.deepcopy(self.currdatal[(index+1):])
        self.datas.append(data)
        self.currdatal = copy.deepcopy(self.currdatal[:index])
        #####
        #pl = copy.copy(self.currpl)
        pl = elel.fcp(self.currpl)
        ####
        self.pls.append(pl)
        self.currpl.pop(-1)
        #####
        attribl = copy.deepcopy(self.currattribl)
        if(self.attrib_pl):
            tl = self.attrl2tl(attribl)
            self.attribs.append(tl)
        else:
            dl = self.attrl2dl(attribl)
            self.attribs.append(dl[-1])
        self.currattribl.pop(-1)
        #####
    def characters(self, data):
        #pl = copy.copy(self.currpl)
        pl = elel.fcp(self.currpl)
        self.currdatal.append((pl,data))
        self.texts_inseq.append((pl,data))


def edfs_traverse_sax(root):
    '''
        | Same as class EDFS_SAX ,just return the object(include .pls , .attribs ,.datas, .texts_inseq, .tags......)
        | using default_wfs_handler
    '''
    rslt = EDFS_SAX()
    lxml.sax.saxify(root, rslt)
    return(rslt)

def edfspls_sax(root):
    '''
        | pathlist-sequence of  depth-first-traverse  
          
        
        :param  lxml.etree._Element root: 
            lxml-etree-element
        :return list:
            list of pathlists  in depth-first-traverse-sequence
    
    ::
    
        html_str = fs.rfile("./test.html")
        root = LXHTML(html_str)
        pls = engine.edfspls(root)
        utils.parr(pls[:10])
        >>>
        ['html', 'head', 'script']
        ['html', 'head', 'script']
        ['html', 'head', 'meta']
        ['html', 'head', 'meta']
        ['html', 'head', 'meta']
        ['html', 'head', 'link']
        ['html', 'head', 'link']
        ['html', 'head', 'link']
        ['html', 'head', 'link']
        ['html', 'head', 'link']
        >>>
        utils.parr(pls[-10:])
        ['html', 'body', 'div', 'div', 'div', 'script']
        ['html', 'body', 'div', 'div', 'div']
        ['html', 'body', 'div', 'div']
        ['html', 'body', 'div', 'div', 'p']
        ['html', 'body', 'div', 'div', 'p', 'a']
        ['html', 'body', 'div', 'div', 'p']
        ['html', 'body', 'div', 'div']
        ['html', 'body', 'div']
        ['html', 'body']
        ['html']
        >>>
        
    '''
    return(edfs_traverse_sax(root).pls)
#



class BEAUTIFY(ContentHandler):
    @classmethod
    def indent(cls,pl,**kwargs):
        if("fixed_indent" in kwargs):
            fixed_indent = kwargs['fixed_indent']
        else:
            fixed_indent = True
        if(fixed_indent):
            if("tab_width" in kwargs):
                tab_width = kwargs['tab_width']
            else:
                tab_width = 4
            padding = "\x20" * tab_width * pl.__len__() 
        else:
            sc = elel.reduce_left(pl,lambda lngth,ele:(lngth+ele.__len__()),0) + 2 * pl.__len__()
            padding = "\x20" * sc
        return(padding)
    @classmethod
    def attr2tl(cls,attrl):
        tl = []
        for i in range(attrl.__len__()):
            attr = attrl[i]
            if(attr.__len__() == 0):
                tl.append(tuple([]))
            else:
                tl.append((attr[0][1],attr[1]))
        return(tl)
    @classmethod
    def attrt2s(cls,t):
        k = t[0]
        v = html.escape(t[1])
        return(k+'="'+v+'"')
    @classmethod
    def attrtl2str(cls,tl):
        if(tl.__len__() ==0):
            s = ""
        else:
            arr = elel.mapv(tl,cls.attrt2s,[])
            s = elel.join(arr,"\x20")
        return(s)
    @classmethod
    def creat_start_tag_str(cls,tag,tlattr,padding):
        s = "<"+tag+"\x20" + cls.attrtl2str(tlattr)
        s = s.strip("\x20")
        s = s +">"
        return(padding+s+"\n")
    @classmethod
    def creat_end_tag_str(cls,tag,padding):
        s = "</"+tag+">"
        return(padding+s+"\n")
    @classmethod
    def creat_text_node_str(cls,s,padding):
        lines = s.split('\n')
        lines = elel.mapv(lines,lambda ele:(padding+ele),[])
        s = elel.join(lines,"\n")
        return(s+"\n")
    def __init__(self,**kwargs):
        self.s = ""
        self.currpl =[]
        self.kwargs= kwargs
        if("highlight" in kwargs):
            self.highlight = kwargs['highlight']
        else:
            self.highlight = {}
    def startElementNS(self, name, qname, attributes):
        tlattr = self.attr2tl(attributes.items())
        padding = self.indent(self.currpl,**self.kwargs)
        self.s = self.s + self.creat_start_tag_str(qname,tlattr,padding)
        self.currpl.append(qname)
    def endElementNS(self, ns_name, qname):
        self.currpl.pop(-1)
        padding = self.indent(self.currpl,**self.kwargs)
        self.s = self.s + self.creat_end_tag_str(qname,padding)
    def characters(self, data):
        padding = self.indent(self.currpl,**self.kwargs)
        s = data.replace("\r","")
        s = s.strip("\n").strip("\x20").strip("\n")
        if(s ==""):
            pass
        else:
            s = self.creat_text_node_str(s,padding)
            regex = re.compile("(.*\n)([\x20]*?)")
            allms = regex.findall(s)
            allms = elel.mapv(allms,lambda s:s[0])
            s = elel.join(allms,"")
            self.s = self.s + html.escape(s)

def s2root(html_str):
    root = LXHTML(html_str)
    return(root)

def f2root(fn):
    html_str = fs.rfile(fn)
    root = LXHTML(html_str)
    return(root)


def sbeautify(html_str,**kwargs):
    root = LXHTML(html_str)
    return(beautify(root,**kwargs))

def fbeautify(fn,**kwargs):
    html_str = fs.rfile(fn)
    root = LXHTML(html_str)
    return(beautify(root,**kwargs))

def beautify(root,**kwargs):
    '''
        | Beautity html output
        
        :param  lxml.etree._Element root: 
            lxml-etree-element
        :param  bool kwargs["fixed_indent]": 
            default True
            fixed_indent, if False ,indent based on tag-string-width
        :param  in tab_width: 
            default 4
            used for fixed_indent
        :return str:
            beautified html_str
        
        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            html_str = engine.beautify(root)
            print(html_str[:480])
            >>>
            <html lang="zh-cn">
                <head>
                    <script async="" src="https://www.googletagmanager.com/gtag/js?id=UA-878633-1">
                    </script>
                    <script>
                        window.dataLayer = window.dataLayer || [];
                    </script>
                    <meta charset="gbk">
                    </meta>
                    <meta name="robots" content="all">
                    </meta>
                    <meta name="author" content="w3school.com.cn">
                    </meta>
                    <link rel="stylesheet" type="text/css" href="/c5_20171220.css">
            >>>
            html_str = engine.beautify(root,fixed_indent=False)
            print(html_str[:480])
            print(html_str[:550])
            <html lang="zh-cn">
                  <head>
                        <script async="" src="https://www.googletagmanager.com/gtag/js?id=UA-878633-1">
                        </script>
                        <script>
                                window.dataLayer = window.dataLayer || [];
                        </script>
                        <meta charset="gbk">
                        </meta>
                        <meta name="robots" content="all">
                        </meta>
                        <meta name="author" content="w3school.com.cn">
                        </meta>
                        <link rel="stylesheet" type="text/css" href="/c5_20171220.css">
            >>>
    '''
    handler = BEAUTIFY(**kwargs)
    lxml.sax.saxify(root, handler)
    return(handler.s.strip("\n"))




######

def diff_value_pls(pls0,pls1):
    rslt = []
    lngth = pls0.__len__()
    for i in range(lngth):
        ele = pls0[i]
        cond = (ele in pls1)
        if(cond):
            pass
        else:
            rslt.append(ele)
    return(rslt)


def group_by_length(pls):
    d = {}
    lngth = len(pls)
    for i in range(lngth):
        pl = pls[i]
        pl_len = len(pl)
        if(pl_len in d):
            d[pl_len].append(pl)
        else:
            d[pl_len] = [pl]
    return(d)


#####

def new_edfs_ele():
    d = {}
    d["edfs_seq"] = None
    d["parent_edfs_seq"] = None
    d["pl"] = None
    d["depth"] = None
    return(d)

def edfspls2edfs_ele_list(edfspls,root_pl_len=1):
    rslt = []
    lngth= len(edfspls)
    for i in range(lngth):
        d = new_edfs_ele()
        d["edfs_seq"] = i
        d["pl"] = edfspls[i]
        d["depth"] = len(d["pl"]) - root_pl_len
        rslt.append(d)
    return(rslt)



def group_by_length_edfs_ele_list(edfs_ele_list,root_pl_len=1):
    d = {}
    lngth = len(edfs_ele_list)
    for i in range(lngth):
        pl = edfs_ele_list[i]['pl']
        if(pl == None):
            pl_len = edfs_ele_list[i]["depth"]+1
        else:
            pl_len = len(pl)
        if(pl_len in d):
            d[pl_len].append(edfs_ele_list[i])
        else:
            d[pl_len] = [edfs_ele_list[i]]
    return(d)


def fill_parent_edfs_seq(edfs_ele_list):
    '''
        一个元素的parent一定在前一层
        end深度优先搜索,一个元素的parent一定是第一个序号大于子节点的元素
    '''
    groups = group_by_length_edfs_ele_list(edfs_ele_list)
    kl =list(groups.keys())
    kl.sort()
    kl.reverse()
    for i in range(len(kl)-1):
        k = kl[i]
        layer = groups[k]
        prev_layer = groups[kl[i+1]]
        for each in layer:
            edfs_seq = each['edfs_seq']
            #each_plen = len(each['pl']) 
            lngth = len(prev_layer)
            si = 0
            for j in range(si,lngth):
                prev_each = prev_layer[j]
                prev_edfs_seq = prev_each['edfs_seq']
                if(prev_edfs_seq > edfs_seq):
                    #prev_each_plen = len(prev_each['pl'])
                    #if(prev_each_plen == each_plen - 1):
                    each['parent_edfs_seq'] = prev_edfs_seq
                    si = j
                    break
                    #else:
                    #    pass
                else:
                    pass
    return((edfs_ele_list,groups))


#####

def edfspls2plmat(edfspls,root_pl_len=1):
    edfs_ele_list = edfspls2edfs_ele_list(edfspls,root_pl_len=root_pl_len)
    edfs_ele_list,groups = fill_parent_edfs_seq(edfs_ele_list)
    mat =[]
    size = max(list(groups.keys()))
    mat = elel.init(size,[])
    for k in groups:
        depth = k - 1
        layer = groups[k]
        mat[depth].extend(layer)
    return(mat)

def edfspls2wfspls(edfspls):
    eplmat = edfspls2plmat(edfspls)
    edfsl = elel.mat2wfs(eplmat)
    wfspls =  elel.mapv(edfsl,lambda ele:ele['pl'])
    return(wfspls)

#####



#####

def is_sibling_via_locs(mat,loc1,loc2):
    if(loc1 == loc2):
        return(False)
    else:
        pbreadth1 = mat[loc1[0]][loc1[1]]['pbreadth']
        pbreadth2 = mat[loc2[0]][loc2[1]]['pbreadth']
        cond = (pbreadth1 == pbreadth2)
        return(cond)



def get_rsib_loc(mat,curr_loc):
    depth,breadth = curr_loc
    rsib_breadth = breadth + 1
    layer = mat[depth]
    lngth = len(layer)
    if(rsib_breadth>= lngth):
        return(None)
    else:
        cond = is_sibling_via_locs(mat,curr_loc,[depth,rsib_breadth])
        if(cond):
            return((depth,rsib_breadth))
        else:
            return(None)




def get_parent_loc(mat,curr_loc):
    depth,breadth = curr_loc
    if(curr_loc ==  (0,0)):
        return(None)
    else:
        pbreadth = mat[depth][breadth]['pbreadth']
        return((depth-1,pbreadth))

def find_first_ancestor_rsibloc(mat,curr_loc):
    rsib_loc = get_rsib_loc(mat,curr_loc)
    while(rsib_loc  == None):
        if(curr_loc ==  (0,0)):
            return(None)
        else:
            ploc = get_parent_loc(mat,curr_loc)
            rsib_loc = get_rsib_loc(mat,ploc)
            curr_loc = ploc
    return(rsib_loc)

####################

def sdfsl_from_mat(mat):
    sdfsl = []
    curr_loc = (0,0)
    count = elel.mat2wfs(mat).__len__()
    visited = 0
    while(visited<count):
        sdfsl.append(curr_loc)
        x = curr_loc[0]
        y = curr_loc[1]
        children = mat[x][y]['children']
        if(children.__len__() == 0):
            curr_loc = find_first_ancestor_rsibloc(mat,curr_loc)
        else:
            curr_loc = children[0]
        visited = visited + 1
    return(sdfsl)


#############################

def edfsl_find_first_ancestor_rsibloc(mat,curr_loc,edfsl):
    rsib_loc = get_rsib_loc(mat,curr_loc)
    while(rsib_loc  == None):
        if(curr_loc ==  (0,0)):
            return(None)
        else:
            ploc = get_parent_loc(mat,curr_loc)
            edfsl.append(ploc)
            rsib_loc = get_rsib_loc(mat,ploc)
            curr_loc = ploc
    return(rsib_loc)

#######################################################

def edfsl_from_mat(mat):
    edfsl = []
    curr_loc = (0,0)
    count = elel.mat2wfs(mat).__len__()
    visited = 0
    while(visited<count):
        x = curr_loc[0]
        y = curr_loc[1]
        children = mat[x][y]['children']
        leaf = children.__len__() == 0
        if(leaf):
            # leaf first 
            edfsl.append(curr_loc)
            curr_loc = edfsl_find_first_ancestor_rsibloc(mat,curr_loc,edfsl)
        else:
            curr_loc = children[0]
        visited = visited + 1
    return(edfsl)

###################################


def sdfsl_from_root(root,**kwargs):
    wfs = wfs_traverse(root,**kwargs)
    m = wfs.mat
    m = init_attr(m,"children",[])
    m = fill_children_attr(m)
    sdfsl = sdfsl_from_mat(m)
    return(sdfsl)

def sdfsl_from_root2(root,**kwargs):
    wfs = wfs_traverse(root,**kwargs)
    m = wfs.mat
    m = init_attr(m,"children",[])
    m = fill_children_attr(m)
    sdfsl = sdfsl_from_mat(m)
    return((sdfsl,m))



def sdfspls_etree(root,**kwargs):
    sdfsl = sdfsl_from_root(root,**kwargs)
    sdfspls = elel.mapv(sdfsl,lambda ele:m[ele[0]][ele[1]]['pl'])
    return(sdfspls)


def edfsl_from_root(root,**kwargs):
    wfs = wfs_traverse(root,**kwargs)
    m = wfs.mat
    m = init_attr(m,"children",[])
    m = fill_children_attr(m)
    edfsl = edfsl_from_mat(m)
    return(edfsl)


def edfspls_etree(root,**kwargs):
    edfsl = edfsl_from_root(root,**kwargs)
    edfspls = elel.mapv(edfsl,lambda ele:m[ele[0]][ele[1]]['pl'])
    return(edfspls)

##########################################

def new_sdfs_ele():
    d = {}
    d["sdfs_seq"] = None
    d["parent_sdfs_seq"] = None
    d["pl"] = None
    d["depth"] = None
    return(d)


def sdfspls2sdfs_ele_list(sdfspls,root_pl_len=1):
    rslt = []
    lngth= len(sdfspls)
    for i in range(lngth):
        d = new_sdfs_ele()
        d["sdfs_seq"] = i
        d["pl"] = sdfspls[i]
        d["depth"] = len(d["pl"]) - root_pl_len
        rslt.append(d)
    return(rslt)


group_by_length_sdfs_ele_list = group_by_length_edfs_ele_list


def fill_parent_sdfs_seq(sdfs_ele_list):
    '''
        一个元素的parent一定在前一层
        start深度优先搜索,一个元素的parent一定是第一个序号小于子节点的元素
    '''
    groups = group_by_length_sdfs_ele_list(sdfs_ele_list)
    kl =list(groups.keys())
    kl.sort()
    kl.reverse()
    for i in range(len(kl)-1):
        k = kl[i]
        layer = groups[k]
        prev_layer = groups[kl[i+1]]
        for each in layer:
            sdfs_seq = each['sdfs_seq']
            #each_plen = len(each['pl'])
            lngth = len(prev_layer)
            si = 0
            for j in range(lngth-1,si-1,-1):
                prev_each = prev_layer[j]
                prev_sdfs_seq = prev_each['sdfs_seq']
                if(prev_sdfs_seq < sdfs_seq):
                    #prev_each_plen = len(prev_each['pl'])
                    #if(prev_each_plen == each_plen - 1):
                    each['parent_sdfs_seq'] = prev_sdfs_seq
                    si = j
                    break
                    #else:
                    #    pass
                else:
                    pass
    return((sdfs_ele_list,groups))


def sdfspls2plmat(sdfspls,root_pl_len=1):
    sdfs_ele_list = sdfspls2sdfs_ele_list(sdfspls,root_pl_len=root_pl_len)
    sdfs_ele_list,groups = fill_parent_sdfs_seq(sdfs_ele_list)
    mat =[]
    size = max(list(groups.keys()))
    mat = elel.init(size,[])
    for k in groups:
        depth = k - 1
        layer = groups[k]
        mat[depth].extend(layer)
    return(mat)


def sdfspls2wfspls(sdfspls):
    splmat = sdfspls2plmat(sdfspls)
    sdfsl = elel.mat2wfs(splmat)
    wfspls =  elel.mapv(sdfsl,lambda ele:ele['pl'])
    return(wfspls)

###############################################


def eplmat2dmat(eplmat):
    '''
        #对于每个eplmat  转化成虚拟的dmat
    '''
    dmat = copy.deepcopy(eplmat)
    dmat = init_attr(dmat,"children",[])
    lngth = len(dmat)
    #######root 
    dmat[0][0]['pbreadth'] = None
    #### fill children  via   edfs_seq
    for i in range(0,lngth-1):
        layer = dmat[i]
        next_layer = dmat[i+1]
        si = 0
        for j in range(len(layer)):
            ele = layer[j]
            ele_edfs_seq = ele['edfs_seq']
            for k in range(si,len(next_layer)):
                child_ele = next_layer[k]
                child_ele_parent_edfs_seq = child_ele['parent_edfs_seq']
                if(child_ele_parent_edfs_seq == ele_edfs_seq):
                    ele['children'].append((i+1,k))
                    child_ele['pbreadth'] = j
                else:
                    #eplmat children 是连续的 ,添加完毕
                    si = k
                    break
    ################last layer
    layer = dmat[lngth-1]
    prev_layer = dmat[lngth-2]
    for j in range(len(layer)):
        child_ele = layer[j]
        child_ele_parent_edfs_seq = child_ele['parent_edfs_seq']
        for k in range(0,len(next_layer)):
            ele = prev_layer[k]
            ele_edfs_seq = ele['edfs_seq']
            if(child_ele_parent_edfs_seq == ele_edfs_seq):
                child_ele['pbreadth'] = k
                break
            else:
                pass
    ################
    return(dmat)




def splmat2dmat(splmat):
    dmat = copy.deepcopy(splmat)
    dmat = init_attr(dmat,"children",[])
    lngth = len(dmat)
    #######root 
    dmat[0][0]['pbreadth'] = None
    #### fill children  via   sdfs_seq
    for i in range(0,lngth-1):
        layer = dmat[i]
        next_layer = dmat[i+1]
        si = 0
        for j in range(len(layer)):
            ele = layer[j]
            ele_sdfs_seq = ele['sdfs_seq']
            for k in range(si,len(next_layer)):
                child_ele = next_layer[k]
                child_ele_parent_sdfs_seq = child_ele['parent_sdfs_seq']
                if(child_ele_parent_sdfs_seq == ele_sdfs_seq):
                    ele['children'].append((i+1,k))
                    child_ele['pbreadth'] = j
                else:
                    #splmat children 是连续的 ,添加完毕
                    si = k
                    break
    ################last layer
    layer = dmat[lngth-1]
    prev_layer = dmat[lngth-2]
    for j in range(len(layer)):
        child_ele = layer[j]
        child_ele_parent_sdfs_seq = child_ele['parent_sdfs_seq']
        for k in range(0,len(next_layer)):
            ele = prev_layer[k]
            ele_sdfs_seq = ele['sdfs_seq']
            if(child_ele_parent_sdfs_seq == ele_sdfs_seq):
                child_ele['pbreadth'] = k
                break
            else:
                pass
    ################
    return(dmat)


####################################################################

def depth_groups_to_plmat(groups):
    mat =[]
    size = max(list(groups.keys()))
    mat = elel.init(size,[])
    for k in groups:
        depth = k - 1
        layer = groups[k]
        mat[depth].extend(layer)
    return(mat)


#####################################################################

def edfspls2sdfspls(edfspls):
    eplmat = edfspls2plmat(edfspls)
    dmat = eplmat2dmat(eplmat)
    sdfsl = sdfsl_from_mat(dmat)
    sdfspls = elel.mapv(sdfsl,lambda loc:dmat[loc[0]][loc[1]]['pl'])
    return(sdfspls)


def sdfspls2edfspls(sdfspls):
    splmat = sdfspls2plmat(sdfspls)
    dmat = splmat2dmat(splmat)
    edfsl = edfsl_from_mat(dmat)
    edfspls = elel.mapv(edfsl,lambda loc:dmat[loc[0]][loc[1]]['pl'])
    return(edfspls)

#####################################################################
