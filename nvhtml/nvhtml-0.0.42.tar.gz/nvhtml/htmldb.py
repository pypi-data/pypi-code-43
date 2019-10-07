from lxml.etree import HTML as LXHTML
from lxml.etree import XML as LXML
from xdict.jprint import pdir,pobj

import lxml.sax
from efdir import fs
import elist.elist as elel
import edict.edict as eded
import estring.estring as eses
import spaint.spaint as spaint
from lxml.etree import tostring as nd2str

import sqlite3
#https://www.sqlite.org/lang_expr.html#regexp
import qtable.qtable as qtb
import estring.estring as eses
from pandas.io import sql
import json
import os
import tytycss.tytycss as tyty
import jsbeautifier as jb
import copy
import xxurl.xxurl as xuxu

def get_all_attrib_names(mat):
    attr_names = set({})
    for i in range(mat.__len__()):
        layer = mat[i]
        for j in range(layer.__len__()):
            ele = layer[j]
            anames = list(ele['attrib'].keys())
            for name in anames:
                attr_names.add(name)
    return(list(attr_names))



def get_attrib_name_freqs(mat,attr_names):
    freqs = elel.init(attr_names.__len__(),0)
    for i in range(mat.__len__()):
        layer = mat[i]
        for j in range(layer.__len__()):
            ele = layer[j]
            anames = list(ele['attrib'].keys())
            for name in anames:
                index = attr_names.index(name)
                freqs[index] = freqs[index] + 1
    return(freqs)

def sort_attr_names(mat):
    attr_names = get_all_attrib_names(mat)
    freqs = get_attrib_name_freqs(mat,attr_names)
    attr_names,freqs= elel.batsorted(freqs,attr_names,freqs,reverse=True)
    return((attr_names,freqs))


def show_attr_freq(mat):
    attr_names,freqs = sort_attr_names(mat)
    tbl = eded.kvlist2d(attr_names,freqs)
    pobj(tbl)



CMMN_HIDDEN_ATTRS = ['pl','depth', 'breadth','pbreadth','sibseq', 'samepl_total','samepl_siblings_total','samepl_sibseq', 'samepl_breadth']
CMMN_NORMAL_ATTRS = ['tag', 'text', 'tail','text_intag']
CMMN_CALC_ATTRS = ['outter_html']

CMMN_ATTRS = CMMN_HIDDEN_ATTRS + CMMN_NORMAL_ATTRS + CMMN_CALC_ATTRS


def handle_each_ele(ele,root,beautify=False):
    del ele['mkdir_pth']
    del ele['text_intag']
    d = {}
    pl = ele['pl']
    tail = pl[-1]
    pth = elel.join(pl,"/")
    pth = "/"  + pth
    ele['pl'] = pth
    #LXML 解析后的缺点是不能获取在原始文件中的位置
    #if(tail[0]=="<"):
    #    outter_html = "<!--" + ele['text'] +"-->"
    #else:
    #    nds = engine.xpath(root,pth)
    #    nd = nds[ele['samepl_breadth']]
    #    if(beautify):
    #        outter_html = engine.beautify(nd)
    #    else:
    #        outter_html = nd2str(nd).decode("utf-8")
    #d['outter_html'] = outter_html
    #############################
    for k in ele:
        v = ele[k]
        if(k in CMMN_ATTRS):
            k = "_"+k
            d[k] = v
        else:
            attrib = v
            if(attrib == None):
                attrib = {}
            else:
               pass
            for ak in attrib:
                av = attrib[ak]
                av = str(av)
                d[ak] = av
    return(d)


def fmt_mat(mat,root):
    for i in range(mat.__len__()):
        for j in range(mat[i].__len__()):
            ele = mat[i][j]
            mat[i][j] = handle_each_ele(ele,root)
    return(mat)

CMMN_COLUMNS =  [
  '_pl',
  '_breadth',
  '_depth',
  '_pbreadth',
  '_samepl_sibseq',
  '_samepl_breadth',
  '_tag',
  '_sibseq',
  '_text',
  '_tail'
]

def get_ele_vl(ele,columns):
    for k in columns:
        if(k in ele):
            pass
        else:
            ele[k] = None
    vl = eded.vlviakl(ele,columns)
    return(vl)


def get_dfmat(mat,columns):
    wfsl = elel.mat2wfs(mat)
    dfmat = elel.mapv(wfsl,get_ele_vl,[columns])
    return(dfmat)


def get_df(dfmat,columns):
    df = qtb.Qtable(mat=dfmat,index=elel.init_range(0,dfmat.__len__(),1),columns=columns)
    return(df)


def find_all_via_attr(df,attr):
    '''
        # >>> df_internal.loc[df_internal['@tag@']=='style'].index
        # Int64Index([41], dtype='int64')
        # >>>
    '''
    df_internal = df.df
    l = list(df_internal.loc[df_internal[attr].notnull()][attr])
    return(l)


def show_columns(df):
    pobj(list(df.df.columns))

def df_row(df,rownum):
    df_internal = df.df
    return(df_internal.loc[rownum].dropna())

def row2d(row):
    '''
        pobj(_row2d(_row(df_internal,35)))
    '''
    kl = list(row.index)
    vl = list(row.values)
    return(eded.kvlist2d(kl,vl))


def df_col(df,colname):
    '''
        list(col.columns)
        list(col.values)
    '''
    df_internal = df.df
    return(df_internal[colname].dropna())


def df2sqlite(df,dbname,tbname="tb_html"):
    df_internal = df.df
    cnx = sqlite3.connect(dbname)
    sql.to_sql(df_internal, name=tbname, con=cnx)
    return(cnx)


