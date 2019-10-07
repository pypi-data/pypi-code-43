from lxml.etree import HTML as LXHTML
from lxml.etree import XML as LXML
from xdict.jprint import pdir,pobj
from nvhtml import txt
from nvhtml import lvsrch
from nvhtml import fs
from nvhtml import engine
from nvhtml import utils
from nvhtml.consts import *


import lxml.sax
import argparse
from efdir import fs
import elist.elist as elel
import edict.edict as eded
import estring.estring as eses
import spaint.spaint as spaint

#import qtable.qtable as qtb
#from pandas.io import sql
#import sqlite3

import math
import copy

import re



def get_ansi_colors_vl():
    ANSI_COLORS_VL = elel.init_range(1,231,1)
    ANSI_COLORS_VL.remove(15)
    ANSI_COLORS_VL.remove(16)
    # vl_odds = elel.select_odds(ANSI_COLORS_VL)
    # vl_evens = elel.select_evens(ANSI_COLORS_VL)
    # vl_evens.reverse()
    # ANSI_COLORS_VL = vl_odds + vl_evens
    return(ANSI_COLORS_VL)


ANSI_COLORS_VL = get_ansi_colors_vl()

TAGS,_ = eded.d2kvlist(TAG_DESCS)
TAGS.append('<comment>')
TAGS.append('svg')

TAG_COLOR_MD = eded.kvlist2d(TAGS,ANSI_COLORS_VL)



def modi_children_s0(ele):
    ele['children'] = []
    return(ele)

def del_unecessary(ele):
    ele = eded.sub_algo(ele,['breadth','depth','pbreadth','samepl_sibseq','samepl_breadth','tag','sibseq','width','children'])
    return(ele)



def scan_s0(mat):
    mat = elel.mat_mapv(mat,modi_children_s0)
    mat = elel.mat_mapv(mat,del_unecessary)
    mat = engine.fill_children_attr(mat)
    return(mat)

# 先不调整宽度


# display_mat
def parr(arr,*args):
    args = list(args)
    if(args.__len__()==0):
        pass
    else:
        try:
            arr = elel.mat_mapv(arr,lambda ele:eded.sub_algo(ele,args))
        except:
            arr = elel.mapv(arr,lambda ele:eded.sub_algo(ele,args))
    elel.for_each(arr,print)


def creat_display_mat(mat):
    display_mat = [[{"loc":(0,0),"empty":False}]]
    depth = len(mat)
    for i in range(0,depth-1):
        layer = display_mat[i]
        breadth = len(layer)
        next_display_layer = []
        for j in range(breadth):
            ele = layer[j]
            loc = ele["loc"]
            pointed_ele = mat[loc[0]][loc[1]]
            children_locs = pointed_ele['children']
            if(len(children_locs)  == 0): # if the pointed mat-ele have no chilren
                next_display_layer.append({"loc":ele['loc'],"empty":True}) 
            else:
                disp = elel.mapv(children_locs,lambda loc:{"loc":loc,"empty":False,})
                next_display_layer.extend(disp)
        display_mat.append(next_display_layer)
    return(display_mat)

####################################################################################################

####################################################################################################
def modi_width_s0(ele):
    '''
        初始化宽度,左右各一个空格
    '''
    width = len(ele['tag'])
    width = width + 2
    ele['width'] = width
    return(ele)
####################################################################################################

####################################################################################################
def sum_children_width(children):
    lngth = children.__len__()
    width = 0
    for i in range(lngth):
        child = children[i]
        width = width + child['width'] + 1
    width = width - 1
    return(width)

def get_children_eles(ele,mat):
    children_locs = ele['children']
    children_eles = elel.mapv(children_locs,lambda child_loc:mat[child_loc[0]][child_loc[1]])
    return(children_eles)

# from bottom to top  保证所有父元素大于子元素宽度之和

def modi_width_s1(ele,mat):
    '''
         from bottom to top  保证所有父元素大于子元素宽度之和
    '''
    children_eles = get_children_eles(ele,mat)
    children_eles = elel.sortDictList(children_eles,cond_keys=['width'])
    width = ele['width']
    lngth = children_eles.__len__()
    if(lngth == 0):
        pass
    else:
        children_width_sum = sum_children_width(children_eles)
        if(width < children_width_sum):
            ele['width'] = children_width_sum
        else:
            pass
    return(ele)

def scan_s1(mat):
    depth = len(mat)
    for i in range(depth-1,-1,-1):
        layer = mat[i]
        breadth = len(layer)
        for j in range(breadth):
            ele = layer[j]
            ele = modi_width_s1(ele,mat)
            mat[i][j] = ele
    return(mat)




####################################################################################################
####################################################################################################

# from top to bottom  保证所有 子元素宽度之和 等于  父元素宽度

def modi_width_s2(ele,mat):
    children_eles = get_children_eles(ele,mat)
    children_eles = elel.sortDictList(children_eles,cond_keys=['width'])
    width = ele['width']
    lngth = children_eles.__len__()
    if(lngth == 0):
        pass
    else:
        children_width_sum = sum_children_width(children_eles)
        if(width > children_width_sum):
            lefted = ele['width']
            q = ele['width'] // lngth
            c = 0
            for i in range(lngth):
                child_width = children_eles[i]['width']
                lefted  = lefted - child_width
                if(child_width>=q):
                    pass
                else:
                    c = c + 1
            c1 = 0
            r1 = lefted % c
            q1 = lefted // c
            for i in range(lngth):
                child_width = children_eles[i]['width']
                if(child_width>q):
                    pass
                else:
                    children_eles[i]['width'] = children_eles[i]['width'] + q1
                    if(c1<r1):
                        children_eles[i]['width'] = children_eles[i]['width'] + 1
                    else:
                        pass
                    c1 = c1 + 1
        else:
            pass
    return(ele)




def scan_s2(mat):
    depth = len(mat)
    for i in range(0,depth-1):
        layer = mat[i]
        breadth = len(layer)
        for j in range(breadth):
            ele = layer[j]
            ele = modi_width_s2(ele,mat)
            mat[i][j] = ele
    return(mat)




###############################################

def modi_display_str_s0(ele):
    tag_lngth = len(ele['tag'])
    width = ele['width']
    lefted = width - tag_lngth
    pre = math.floor(lefted /2)
    post = math.ceil(lefted /2)
    s = " "*pre + ele['tag'] + " "*post
    ele['display_str'] = s
    try:
        ele['display_color'] = TAG_COLOR_MD[ele['tag']]
    except:
        ele['display_color'] = 15
    else:
        pass
    return(ele)



def scan_s3(mat):
    depth = len(mat)
    for i in range(0,depth):
        layer = mat[i]
        breadth = len(layer)
        for j in range(breadth):
            ele = layer[j]
            ele = modi_display_str_s0(ele)
            mat[i][j] = ele
    return(mat)
            

#
def scan_disp_mat_s0(disp_mat,mat,color_enable=False):
    depth = len(disp_mat)
    for i in range(0,depth):
        layer = disp_mat[i]
        breadth = len(layer)
        for j in range(breadth):
            ele = disp_mat[i][j]
            loc = ele['loc']
            s  = mat[loc[0]][loc[1]]["display_str"]
            color  = mat[loc[0]][loc[1]]["display_color"]
            if(ele['empty']):
                s = " "*len(s)
                ele = s
            else:
                ele = s
            if(color_enable):
                disp_mat[i][j]= spaint.slpaint(ele,color,rtrn=True)
            else:
                disp_mat[i][j]= ele
    return(disp_mat)

#######################3


####################################################


def get_orig_length(line):
    line = re.sub("\x1b\[.*?0m","",line)
    return(len(line))

def show_tag_tb(disp_mat):
    s = ""
    layer = disp_mat[0]
    line = "|" + elel.join(layer,"|") +  "|"
    orig_length = get_orig_length(line)
    boundary = "-" * orig_length
    print(boundary)
    print(line)
    print(boundary)
    s = s + boundary +"\n" + line +"\n" + boundary +"\n"
    depth = len(disp_mat)
    for i in range(1,depth):
        layer = disp_mat[i]
        breadth = len(layer)
        line = "|" + elel.join(layer,"|") +  "|"
        print(line)
        print(boundary)
        s = s + line +"\n"+ boundary + "\n"
    return(s)

