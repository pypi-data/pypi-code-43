from lxml.etree import HTML as LXHTML
from lxml.etree import XML as LXML
from xdict.jprint import pdir,pobj
from nvhtml import txt
from nvhtml import lvsrch
from nvhtml import fs
from nvhtml import engine
from nvhtml import utils
from nvhtml import dmat_writer as dmwr
import lxml.sax
import argparse
from efdir import fs
import elist.elist as elel
import estring.estring as eses
import spaint.spaint as spaint
from xml.sax.handler import ContentHandler

import copy
import re


####html to easy format
# #     comment
# -     attrib     属性有两种写法,直接跟或者当作子元素,换行的话会用空格连接
# .     text and tail
# |     text and tail content can multiline

####################################################################
#html
#    head
#        -id menu-item-27961
#        -class
#            qtranxs-lang-menu-item
#            qtranxs-lang-menu-item-ca
#            menu-item
#            menu-item-type-custom
#            menu-item-object-custom
#            menu-item-27961
#        .text
#            |hello
#            |hi
#            |hao
#            |hihihi
#        .tail
#            |this is a tail
#        meta
#            -http-equiv X-UA-Compatible
#            -content IE=edge,chrome=1
#        meta
#            -name viewport
#            -content
#                width=device-width,
#                user-scalable=yes,
#                initial-scale=1.0,
#                minimum-scale=1.0,
#                maximum-scale=3.0
#        meta
#            -http-equiv Content-Type
#            -content text/html; charset=UTF-8
#        link
#        link
#    body
#        div
#            li
#            li
#            li
#        div
#            li
#            li
#        div
#    #comment
#        .text
#            |this is a comment
####################################################################


from lxml.etree import HTML as LXHTML
from lxml.etree import XML as LXML
from xdict.jprint import pdir,pobj
from nvhtml import txt
from nvhtml import lvsrch
from nvhtml import fs
from nvhtml import engine
from nvhtml import utils
from nvhtml import dmat_writer as dmwr
import lxml.sax
import argparse
from efdir import fs
import elist.elist as elel
import estring.estring as eses
import edict.edict as eded
import spaint.spaint as spaint
from xml.sax.handler import ContentHandler

import copy
import re


#htmlrs
#reStructuredHtml
#.rshtml

'''
    #     comment
    -     attrib  attribute could be multilines
    .     text and tail
    |     text and tail content could be multilines 
'''


INDENT = "    "
CNTNT_SP = " "

def parr(arr):
    elel.for_each(arr,print)


def unpack_line(line,sdfs_seq,indent=INDENT):
    indent_lngth =  len(indent)
    line_lngth = len(line)
    depth = 0
    for i in range(0,line_lngth,indent_lngth):
        sec = line[i:i+indent_lngth]
        if(sec == indent):
            depth = depth + 1
        else:
            break
    return({
        "depth":depth,
        "cntnt":line[i:],
        "sdfs_seq":sdfs_seq,
        "pl":None,
        "parent_sdfs_seq":None,
        "_del":False
    })



def get_line_cntnt_type(line_cntnt):
    type = line_cntnt[0]
    if(type == "#"):
        return("comment")
    elif(type == "-"):
        return("attrib")
    elif(type == "."):
        return("txt_head")
    elif(type == "|"):
        return("txt_line")
    else:
        return("tag")

def split_at_first_space(s,sp=CNTNT_SP):
    try:
        index = s.index(sp)
    except:
        head = s
        tail = ""
    else:
        head = s[:index]
        tail = s[index+1:]
    return((head,tail))

def dcd_direct_cntnt(line_cntnt):
    type = get_line_cntnt_type(line_cntnt)
    if(type == "tag"):
        line_left = line_cntnt
    else:
        line_left = line_cntnt[1:]
    head,tail = split_at_first_space(line_left)
    if(type == "tag"):
        return({
            "type":"tag",
            "head":head,
            "tail":tail
        })
    if(type == "txt_head"):
        return({
            "type":"txt_head",
            "head":head,
            "tail":tail
        })
    if(type == "txt_line"):
        return({
            "type":"txt_line",
            "head":head,
            "tail":tail
        })
    if(type == "comment"):
        return({
            "type":"comment",
            "head":head,
            "tail":tail
        })
    else:
        return({
            "type":"attrib",
            "head":head,
            "tail":tail
        })

def group_by_depth(unpacked_lines):
    d = {}
    for each in unpacked_lines:
        depth = each["depth"]
        if(depth in d):
            d[depth].append(each)
        else:
            d[depth] = [each]
    return(d)



def lines2dmat(lines):
    sdfs_ele_list = elel.mapiv(lines,lambda i,v:unpack_line(v,i))
    sdfs_ele_list,groups = engine.fill_parent_sdfs_seq(sdfs_ele_list)
    ####splmat
    mat = engine.depth_groups_to_plmat(groups)
    ####dmat
    mat = engine.splmat2dmat(mat)
    return(mat)


def handle_s0(dmat,sp=CNTNT_SP):
    lngth = len(dmat)
    for i in range(lngth):
        layer = dmat[i]
        for j in range(len(layer)):
            ele = layer[j]
            ele = eded.sub_algo(ele,['cntnt','children','sdfs_seq','parent_sdfs_seq','_del'])
            ele['attrib'] = {}
            d = dcd_direct_cntnt(ele['cntnt'])
            ele["_type"] = d['type']
            if(d['type'] == "tag"):
                ele['tag'] = d['head']
            elif(d['type'] == "comment"):
                ele['tag'] = "<comment>"
            elif(d['type'] == "txt_head"):
                ele[d['head']] = d['tail']
                ele["_type"] = d['head']
            elif(d['type'] == "txt_line"):
                ele["txt_line"] = d['head']+CNTNT_SP+d['tail']
            elif(d['type'] == "attrib"):
                ele['attrib'][d['head']] = d['tail']
            else:
                pass
            del ele['cntnt']
            dmat[i][j] = ele
    return(dmat)


def handle_s1(dmat,sp=CNTNT_SP):
    lngth = len(dmat)
    for i in range(lngth - 1):
        layer = dmat[i]
        for j in range(len(layer)):
            ele = layer[j]
            type = ele['_type']
            children = ele['children']
            if(type ==  "text"):
                #concat all txt_lines  with "\n"
                lns = elel.mapv(children,lambda child:dmat[child[0]][child[1]]['txt_line'])
                if(len(lns)>0):
                    if(ele['text'] == ""):
                        ele['text'] = elel.join(lns,"\n")
                    else:
                        ele['text'] = ele['text'] + "\n" +elel.join(lns,"\n")
                else:
                    pass
                #
                for k in range(len(children)):
                    loc = children[k]
                    dmat[loc[0]][loc[1]]['_del'] = True
            elif(type ==  "tail"):
                #concat all txt_lines  with "\n"
                lns = elel.mapv(children,lambda child:dmat[child[0]][child[1]]['txt_line'])
                if(len(lns)>0):
                    if(ele['tail'] == ""):
                        ele['tail'] = elel.join(lns,"\n")
                    else:
                        ele['tail'] = ele['tail'] + "\n" +elel.join(lns,"\n")
                else:
                    pass
                #
                for k in range(len(children)):
                    loc = children[k]
                    dmat[loc[0]][loc[1]]['_del'] = True
            elif(type == "attrib"):
                #concat all attrib  with " "
                lns = elel.mapv(children,lambda child:dmat[child[0]][child[1]]['tag'])
                attr = list(ele['attrib'].keys())[0]
                if(len(lns)>0):
                    ele['attrib'][attr] = ele['attrib'][attr] + " " +elel.join(lns," ")
                else:
                    pass
                #
                for k in range(len(children)):
                    loc = children[k]
                    dmat[loc[0]][loc[1]]['_del'] = True
            else:
                pass
    return(dmat)


def handle_s2(dmat,sp=CNTNT_SP):
    lngth = len(dmat)
    for i in range(lngth):
        layer = dmat[i]
        new_layer = elel.cond_select_values_all(layer, cond_func=lambda ele:ele['_del']==False)
        dmat[i] = new_layer
    return(dmat)


def handle_s3(dmat,sp=CNTNT_SP):
    dmat = engine.splmat2dmat(dmat)
    lngth = len(dmat)
    for i in range(lngth-1,0,-1):
        layer = dmat[i]
        player = dmat[i-1]
        for j in range(len(layer)):
            ele=layer[j]
            pele = player[ele['pbreadth']]
            if(ele['_type'] == "text"):
                pele['text'] = ele['text']
                ele['_del'] = True
            elif(ele['_type'] == "tail"):
                pele['tail'] = ele['tail']
                ele['_del'] = True
            elif(ele['_type'] == "attrib"):
                k = list(ele['attrib'].keys())[0]
                pele['attrib'][k] = ele['attrib'][k]
                ele['_del'] = True
            else:
                pass
    return(dmat)

handle_s4 = handle_s2

def handle_s5(dmat,sp=CNTNT_SP):
    dmat = engine.splmat2dmat(dmat)
    lngth = len(dmat)
    for i in range(lngth-1,-1,-1):
        layer = dmat[i]
        for j in range(len(layer)):
            ele=layer[j]
            if("text" in ele):
                pass
            else:
                ele['text'] =""
            if("tail" in ele):
                pass
            else:
                ele['tail'] =""
    return(dmat)

def get_dmat(s):
    s = s.strip("\n")
    lines = s.split("\n")
    dmat = lines2dmat(lines)
    dmat = handle_s0(dmat)
    dmat = handle_s1(dmat)
    dmat = handle_s2(dmat)
    dmat = handle_s3(dmat)
    dmat = handle_s4(dmat)
    dmat = handle_s5(dmat)
    return(dmat)

def rsh2html(rsh):
    dmat = get_dmat(rsh)
    html_txt = dmwr.dmat2html(dmat)
    return(html_txt)

def tag2lines(ele,lines):
    tag = ele['tag']
    tag_indent = INDENT * ele['depth']
    if(tag == "<comment>"):
        tag_line = tag_indent + "comment"
    else:
        tag_line = tag_indent + tag
    lines.append(tag_line)
    return(lines)

def attrib2lines(ele,lines):
    attrib = ele['attrib']
    if(len(attrib)>0):
        attr_indent = INDENT * (ele['depth'] + 1)
        for k in attrib:
            attr_line = attr_indent + "-" + k +CNTNT_SP + attrib[k]
            lines.append(attr_line)
    else:
        pass
    return(lines)


def fmt_txt(s,indent):
    if(s == None):
        s = ""
    else:
        pass
    s = eses.lstrip(s,"\n",1)
    si = len(indent)
    if(s[:si] == indent):
        s = s[si:]
    else:
        pass
    return(s)


def text2lines(ele,lines):
    text = ele['text']
    if(text == None):
        text = ""
    else:
        pass
    #text 会缩进ele['depth']+1
    #去掉行首缩进
    tail_indent = INDENT * (ele['depth'] + 1)
    tail_lines = text.split("\n")
    tail_lines = elel.mapv(tail_lines,fmt_txt,[tail_indent])
    tail_lines = elel.cond_select_values_all(tail_lines,cond_func=lambda ele:len(ele)>0)
    #text 对应在rshtml中没有text的情况
    if(len(tail_lines)==1):
        if(tail_lines[0] == INDENT * ele['depth']):
            return(lines)
        else:
            pass
    else:
         pass
    #
    tail_lines = elel.mapv(tail_lines,lambda line:tail_indent+INDENT+"|"+line)
    if(len(tail_lines)>0):
        head_indent = INDENT * (ele['depth'] + 1)
        head_line = head_indent + ".text"
        lines.append(head_line)
        lines.extend(tail_lines)
    else:
        pass
    return(lines)

def tail2lines(ele,lines,dmat,loc):
    tail = ele['tail']
    if(tail == None):
        tail = ""
    else:
        pass
    ########tail有特殊情况,如果是最后一个没有rsib
    cond = engine.get_rsib_loc(dmat,loc)
    if(cond == None):
        s = INDENT * (ele['depth'] - 1)
        lngth = len(s)
        if(tail[-lngth:] == s):
            tail = tail[:(-lngth-1)]
        else:
            pass
    else:
        pass
    ##########
    #tail 的尾部也要消除
    #lxml计算出的缩进:尾部不继续缩进，所以尾部与tag缩进一致
    tail_indent = INDENT * ele['depth'] 
    tail_lines = tail.split("\n")
    tail_lines = elel.mapv(tail_lines,fmt_txt,[tail_indent])
    tail_lines = elel.cond_select_values_all(tail_lines,cond_func=lambda ele:len(ele)>0)
    #rshtml 要求的缩进
    tail_lines = elel.mapv(tail_lines,lambda line:tail_indent+INDENT*2+"|"+line)
    if(len(tail_lines)>0):
        head_indent = INDENT * (ele['depth'] + 1)
        head_line = head_indent + ".tail"
        lines.append(head_line)
        lines.extend(tail_lines)
    else:
        pass
    return(lines)

def html2rsh(html_txt):
    root = LXHTML(html_txt)
    sdfsl,dmat = engine.sdfsl_from_root2(root)
    lines = []
    for i in range(len(sdfsl)):
        loc = sdfsl[i]
        ele = dmat[loc[0]][loc[1]]
        lines = tag2lines(ele,lines)
        lines = attrib2lines(ele,lines)
        lines = text2lines(ele,lines)
        lines = tail2lines(ele,lines,dmat,loc)
    rsh = elel.join(lines,"\n")
    return(rsh)


