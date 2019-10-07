
from lxml.etree import HTML as LXHTML
from lxml.etree import XML as LXML
from xdict.jprint import pdir,pobj
from nvhtml import txt
from nvhtml import lvsrch
from nvhtml import fs
from nvhtml import engine
from nvhtml import utils
import lxml.sax
import argparse
from efdir import fs
import elist.elist as elel
import estring.estring as eses
import spaint.spaint as spaint

parser = argparse.ArgumentParser()
parser.add_argument('-input','--input_html_file', default="",help="input html file name")
parser.add_argument('-codec','--input_codec', default="utf-8",help="input html file codec")
parser.add_argument('-tgpth','--tag_path', default=".",help="html tag dot path")

#    '''
#        >>> get_dot_path_segs(".")
#        (['//'], '')
#        >>>
#        >>> get_dot_path_segs(".html")
#        (['//'], 'html')
#        >>> get_dot_path_segs("html.")
#        (['/html'], '')
#        >>> get_dot_path_segs("html")
#        ([], 'html')
#        >>>
#        >>> get_dot_path_segs(".a.b.3.c.d.5.e.f")
#        (['//a/b', 3, 'c/d', 5, 'e'], 'f')
#        >>>
#        >>> get_dot_path_segs("a.b.3.c.d.5.e.f")
#        (['/a/b', 3, 'c/d', 5, 'e'], 'f')
#        >>>
#        >>> get_dot_path_segs("a.b.3.c.d.5.e.f.")
#        (['/a/b', 3, 'c/d', 5, 'e/f'], '')
#        >>>
#    '''



def get_dot_path_segs(pth):
    arr =  pth.split(".")
    tail = arr[-1]
    arr  =  arr[:-1]
    segs = []
    if(arr.__len__() == 0):
        pass
    else:
        if(arr[0] ==  ""):
            arr[0] =  "/"
        else:
            pass
        seg = ""
        for i in range(arr.__len__()):
            tag = arr[i]
            try:
                int(tag)
            except:
                seg  = seg + tag + "/"
            else:
                seg = eses.rstrip(seg,"/",1)
                segs.append(seg)
                segs.append(int(tag))
                seg = ""
        if(seg == ""):
            pass
        else:
            seg = eses.rstrip(seg,"/",1)
            segs.append(seg)
        if(segs[0][0]=="/"):
            cond = (segs[0].__len__() == 1)
            if(cond):
                segs[0] = segs[0] = "/" + segs[0]
            else:
                pass
        else:
            segs[0] = "/" + segs[0]
    return((segs,tail))




def get_pre_tail_nodes(pth,root):
    '''
    '''
    #
    segs,tail = get_dot_path_segs(pth)
    #
    node = root
    xpath = ""
    #
    for i in range(0,segs.__len__()):
        seg = segs[i]
        try:
            int(seg)
        except:
            xpath = seg
        else:
            nodes = engine.xpath(node,xpath)
            node = nodes[int(tag)]
            xpath = ""
    if(xpath ==  ""):
        nodes = [node]
    else:
        if(xpath == "//"):
            nodes = [node]
        else:
            nodes = engine.xpath(node,xpath)
    return((nodes,tail))





##############################################
def get_next_layer_tags_via_xpath(root,xpath):
    eles = engine.xpath(root,xpath)
    arr = elel.mapv(eles,lambda ele:ele.getchildren())
    rslt = []
    for i in range(arr.__len__()):
        tmp = arr[i]
        rslt.extend(tmp)
    tags = elel.mapv(rslt,lambda ele:ele.tag)
    return(tags)
####################################################

def get_next_layer_tags(nodes):
    eles = elel.mapv(nodes,lambda ele:ele.getchildren())
    rslt = []
    for i in range(eles.__len__()):
        tmp = eles[i]
        rslt.extend(tmp)
    tags = elel.mapv(rslt,lambda ele:ele.tag)
    return((tags,rslt))





def get_seqs(tags,tail):
    seqs = elel.indexes_all(tags,tail)
    return(seqs)

def get_options(tags,tail):
    rslt = []
    for i in range(tags.__len__()):
        tag = tags[i]
        tag = str(tag)
        cond = tag.startswith(tail)
        if(cond):
            rslt.append(tag)
        else:
            pass
    return(rslt)


args = parser.parse_args()


def is_single_path(pth,root):
    arr = pth.split(".")
    tail =  arr[-1]
    arr = arr[:-1]
    if(arr.__len__()==0):
        return((True,tail))
    else:
        if(arr[0] == ""):
            arr = arr[1:]
        else:
            pass
        if(arr.__len__()==0):
            return((True,tail))
        else:
            return((False,tail))


def is_number_str(s):
    try:
        int(s)
    except:
        return(False)
    else:
        return(True)


def main():
    html_str = fs.rfile(args.input_html_file)
    root = LXHTML(html_str)
    pth = args.tag_path
    #direct root path
    cond,tail= is_single_path(pth,root)
    if(cond):
        if(root.tag == tail):
            print(engine.beautify(root))
            return(None)
        elif(root.tag.startswith(tail)):
            pobj([root.tag])
            return(None)
        else:
            pass
    else:
        pass
    #
    if(pth != "."):
        #
        nodes,tail = get_pre_tail_nodes(pth,root)
        #
        if(tail == ""): 
            lngth = nodes.__len__()
            if(lngth > 1):   #如果当前xpath路径得到的元素不唯一
                pobj(elel.init_range(0,lngth,1))
            else:
                #end with a ".", means search next layer tags
                opts,final_nodes = get_next_layer_tags(nodes)
                pobj(opts)
        elif(is_number_str(tail)):
            seq = is_number_str(tail)
            nd = nodes[seq]
            print(engine.beautify(nd))
        else:
            tags,final_nodes = get_next_layer_tags(nodes)
            seqs = get_seqs(tags,tail)           #how many samepl_seqs
            lngth = seqs.__len__()
            if(lngth == 0):
                opts  = get_options(tags,tail)
                pobj(opts)
            elif(lngth == 1):
                breadth = seqs[0]
                nd = final_nodes[breadth]
                print(engine.beautify(nd))
            else:
                pobj(elel.init_range(0,lngth,1))
    else:
        pobj([root.tag])



#nvhtml_tgpth -input opis.html  -tgpth html.body.div
