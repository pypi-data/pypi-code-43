from bs4 import BeautifulSoup 
import re
import Levenshtein
from zlgg.core import to_arr,ismat
import Levenshtein 
from lmf.dbv2 import db_query
import sys 

import time
import json 
import copy

from collections import OrderedDict
from zlgg.analysis.table import calsep 
from zlgg.extdata.ps import pat 
htmlparser="lxml"




def g_strings(page,krr):

    arr=to_arr(str(page))
    #data=OrderedDict({})
    data={}
    flags=set(range(len(arr)))
    for i in range(len(arr)):
        for j in range(3):
            word=''.join(arr[i:i+j+1])
            if pat(word,krr):
                flags=flags-set(range(i,i+j+1))
                words=re.split(":|：",word)
                k,v=words[0],''.join(words[1:])
                #k=matwhat(k)
                if k not in data.keys():
                    data[k]=v
                else:
                    if not isinstance(data[k],list):
                        arr1=[copy.deepcopy(data[k]),v]
                        data[k]=arr1
                    else:
                        data[k].append(v)
                break
    if data=={}:return page.text.strip()
    tmp=[]
    for i in flags:
        tmp.append(arr[i])
    if len( list(filter(lambda x:len(x)>=3,tmp) ))>=4:return page.text.strip()
    data['general']=tmp

    return data


def g_strings1(tag):
    v='$sep$'.join(filter(lambda x:x!='' ,[w.strip() for w in tag.strings]))
    return v 

def tb1(table,krr):
    #href="http://aqggzy.anqing.gov.cn/jyxx/012001/012001003/20190103/f67eefee-2121-43dc-82f1-968b30837886.html"
    soup=BeautifulSoup(table,htmlparser)
    table=soup.find('table')
    trs=table.find_all('tr')
    #data=OrderedDict({})
    data={}
    i=0
    for tr in trs:
        tds=tr.find_all('td')
        if len(tds)==1 and i==0:continue
        tdl=len(tds)
        if tdl%2!=0:continue
        for j in range(int(tdl/2)):
            k=tds[j*2].text.strip()
            #v=tds[j*2+1].text.strip()
            v=g_strings(tds[j*2+1],krr)
            if k not in data.keys():data[k]=v
            else:
                if not isinstance(data[k],list):
                    arr=[copy.deepcopy(data[k]),v]
                    data[k]=arr
                else:
                    data[k].append(v)
        i=+1
    return data

def tb2(table,krr):
    soup=BeautifulSoup(table,htmlparser)
    table=soup.find('table')
    #data=OrderedDict({})
    data={}
    tdrr=[ tr.find_all('td') for tr in table.find_all('tr') ]

    for i in range( int(len(tdrr)/2)):
        try:
            ktd,vtd=tdrr[2*i],tdrr[2*i+1]
            for j in range(len(ktd)):
                k=ktd[j].text.strip()
                #v=vtd[j].text.strip()
                v=g_strings(vtd[j],krr)
                if k not in data.keys():data[k]=v
                else:
                    if not isinstance(data[k],list):
                        arr=[copy.deepcopy(data[k]),v]
                        data[k]=arr
                    else:
                        data[k].append(v)
        except:
            pass
    return data 


def tb3(page,krr):
    soup=BeautifulSoup(page,htmlparser)
    table=soup.find('table')
    tdarr=[  tr.find_all('td') for tr in  table.find_all('tr')  ] 
    #data=OrderedDict({})
    data={}
    for i in range(len(tdarr)):
        tr=tdarr[i]
        for j in range(len(tr)):
            word=tr[j].text.strip()

            if ismat(word,krr):

                k=word
                v=None
                if j+1<len(tr):
                    hx1_=tr[j+1].text.strip()
                    hx1=g_strings(tr[j+1],krr)

                    if not ismat(hx1_,krr):
                        v=hx1
                    else:
                        if i+1<len(tdarr) and j<len(tdarr[i+1]):
                            hx2_=tdarr[i+1][j].text.strip()
                            hx2=g_strings(tdarr[i+1][j],krr)
                            if not ismat(hx2_,krr):v=hx2
                else:
                    if i+1<len(tdarr):
                        if j<len(tdarr[i+1]):
                            hx2_=tdarr[i+1][j].text.strip()
                            hx2=g_strings(tdarr[i+1][j],krr)
                            if not ismat(hx2_,krr):v=hx2
                if v is not None:
                    if k not in data.keys():data[k]=v
                    else:
                        if not isinstance(data[k],list):
                            arr=[copy.deepcopy(data[k]),v]
                            data[k]=arr
                        else:
                            data[k].append(v)

            else:
                continue
    return data


def tb(page,krr):
    v=calsep(page,krr)
    if v==0:
        data=tb1(page,krr)
    elif v==1:
        data=tb2(page,krr)
    else:
        data=tb3(page,krr)

    return data