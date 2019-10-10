
from bs4 import BeautifulSoup

import collections

import json

import pandas as pd

# import re




from collections import defaultdict






def ext_zhejiangsheng(page,fabu_time,info=None):
    if page is None or page=='':
        return ''

    page=page.replace('<th ','<td ').replace('</th>','</td>').replace('<th>','<td>')

    fabu_time=str(fabu_time)

    if 'jieguo' in info:

        jieguo=json.loads(info)['jieguo']

    else:

        jieguo=''

    soup=BeautifulSoup(page,'html.parser')

    result={}

    # d=collections.defaultdict(lambda :None)
    # d.update(ext_tb1(page))
    d=collections.defaultdict(lambda :None)

    d.update(ext_tb1(str(soup.table)))
    result={

        "xmmc":d['项目名称'],
        "xmdm":d['项目代码'],
        "xmdw":d['项目法人单位'],
        "xmtz":"",
        "xmzt":jieguo,
        "xmdz":"",
        "xmgk":"",
        "fabu_time":fabu_time
        }

    return json.dumps(result,ensure_ascii=False)

def ext_yunnansheng(page,fabu_time,info=None):
    if page is None or page=='':
        return ''

    fabu_time=str(fabu_time)

    soup=BeautifulSoup(page,'html.parser')

    result={}

    tbs=soup.find_all('table')
    d=collections.defaultdict(lambda :None)

    d1=ext_tb1(str(tbs[0]))

    d2=ext_tb1(str(tbs[1]))

    d.update(d1)
    d.update(d2)

    result={

        "xmmc":d['项目名称'],
        "xmdm":d['项目代码'],
        "xmdw":"",
        "xmtz":"",
        "xmzt":d["项目状态"],
        "xmdz":d["建设地点"],
        "xmgk":"",
        "fabu_time":fabu_time
        }

    return json.dumps(result,ensure_ascii=False)

def ext_xiamenshi(page,fabu_time,info=None):
    if page is None or page=='':
        return ''

    fabu_time=str(fabu_time)

    if 'shenpijieguo' in info:

        jieguo=json.loads(info)['shenpijieguo']

    else:

        jieguo=''

    soup=BeautifulSoup(page,'html.parser')

    result={}

    # d=collections.defaultdict(lambda :None)
    # d.update(ext_tb1(page))
    d=collections.defaultdict(lambda :None)

    d.update(ext_tb1(str(soup.table)))

    result={

        "xmmc":d['项目名称'],
        "xmdm":d['中央代码/地方代码'],
        "xmdw":d['项目（法人）单位'],
        "xmtz":"",
        "xmzt":jieguo,
        "xmdz":"",
        "xmgk":"",
        "fabu_time":fabu_time
        }

    return json.dumps(result,ensure_ascii=False)

def ext_sichuansheng(page,fabu_time,info=None):
    if page is None or page=='':
        return ''

    page=page.replace('<th ','<td ').replace('</th>','</td>').replace('<th>','<td>')

    fabu_time=str(fabu_time)

    if 'result' in info:

        jieguo=json.loads(info)['result']

    else:

        jieguo=''

    soup=BeautifulSoup(page,'html.parser')

    result={}

    d=collections.defaultdict(lambda :None)
    d.update(ext_tb1(str(soup.table)))

    result={

        "xmmc":d['项目名称'],
        "xmdm":d['项目代码'],
        "xmdw":d['项目单位'],
        "xmtz":d["项目总投资\n                及资金来源"],
        "xmzt":jieguo,
        "xmdz":d["建设地点详情"],
        "xmgk":d["主要建设内容及规模"],
        "fabu_time":fabu_time
        }

    return json.dumps(result,ensure_ascii=False)

def ext_shanxisheng(page,fabu_time,info=None):
    if page is None or page=='':
        return ''
    fabu_time=str(fabu_time)

    soup=BeautifulSoup(page,'html.parser')

    result={}

    d=collections.defaultdict(lambda :None)
    d.update(ext_tb1(str(soup.table)))

    result={

        "xmmc":d['项目名称：'],
        "xmdm":d['项目代码：'],
        "xmdw":d['单位名称：'],
        "xmtz":d["项目总投资（万元）："]+"(万元)",
        "xmzt":d["审核状态："],
        "xmdz":d["建设地点："],
        "xmgk":d["主要建设规模及内容："],
        "fabu_time":fabu_time
        }

    return json.dumps(result,ensure_ascii=False)

def ext_qinghaisheng(page,fabu_time,info=None):

    if page is None or page=='':return ''

    fabu_time=str(fabu_time)

    soup=BeautifulSoup(page,'html.parser')

    if 'shenpijieguo' in info:

        jieguo=json.loads(info)['shenpijieguo']

    else:

        jieguo=''

    result,d={},{}
    d=collections.defaultdict(lambda :None)

    d.update(ext_tb1(str(soup.table)))

    result={
                "xmmc":d['项目名称'],
                "xmdm":d['项目代码'],
                "xmdw":d['项目法人单位'],
                "xmtz":"",
                "xmzt":jieguo,
                "xmdz":"",
                "xmgk":"",
                "fabu_time":fabu_time
                }

    return json.dumps(result,ensure_ascii=False)

def ext_hubeisheng(page,fabu_time,info=None):

    if page is None or page=='':
        return ''

    fabu_time=str(fabu_time)

    soup=BeautifulSoup(page,'html.parser')

    if 'result' in info:

        jieguo=json.loads(info)['result']

    else:

        jieguo=''
    d=collections.defaultdict(lambda :None)

    d.update(ext_tb1(str(soup.table)))

    result={
                "xmmc":d['项目名称：'],
                "xmdm":d['项目代码：'],
                "xmdw":d['单位名称：'],
                "xmtz":d["项目总投资（万元）："],
                "xmzt":jieguo,
                "xmdz":d['建设地点：'],
                "xmgk":d["主要建设规模及内容："],
                "fabu_time":fabu_time
    }
    return json.dumps(result,ensure_ascii=False)

def ext_henansheng(page,fabu_time,info=None):
    if page is None or page=='':
        return ''
    fabu_time=str(fabu_time)

    soup=BeautifulSoup(page,'html.parser')

    if 'status' in info:

        jieguo=json.loads(info)['status']

    else:

        jieguo=''

    result,d1,d2={},{},{}
    d=collections.defaultdict(lambda :None)
    tbs=soup.find_all('table')
    if len(tbs)>=2:
        d1,d2=ext_tb1(str(tbs[0])),ext_tb1(str(tbs[1]))
    d.update(d1)
    d.update(d2)

    result={
                "xmmc":d['项目名称'],
                "xmdm":d['项目代码'],
                "xmdw":d['单位名称'],
                "xmtz":d["估算总投资(万元)"],
                "xmzt":jieguo,
                "xmdz":d['项目建设地'],
                "xmgk":d["建设规模及内容"],
                "fabu_time":fabu_time
                }

    return json.dumps(result,ensure_ascii=False)

def ext_heilongjiangsheng(page,fabu_time,info=None):
    if page is None or page=='':
        return ''
    page=page.replace('<th ','<td ').replace('</th>','</td>').replace('<th>','<td>')

    fabu_time=str(fabu_time)

    soup=BeautifulSoup(page,'html.parser')

    if 'jieguo' in info:

        jieguo=json.loads(info)['jieguo']

    else:

        jieguo=''

    result,d={},{}
    d=collections.defaultdict(lambda :None)

    d.update(ext_tb1(str(soup.table)))

    result={
                "xmmc":d['项目名称'],
                "xmdm":d['项目代码'],
                "xmdw":d['项目法人单位'],
                "xmtz":"",
                "xmzt":jieguo,
                "xmdz":"",
                "xmgk":"",
                "fabu_time":fabu_time
                }

    return json.dumps(result,ensure_ascii=False)

def ext_hebeisheng(page,fabu_time,info=None):
    if page is None or page=='':
        return ''
    fabu_time=str(fabu_time)

    soup=BeautifulSoup(page,'html.parser')

    if 'jieguo' in info:

        jieguo=json.loads(info)['jieguo']

    else:

        jieguo=''

    result={}

    tbs=soup.find_all('table')

    d=collections.defaultdict(lambda :None)

    d.update(ext_tb1(str(tbs[1])))

    result={
                "xmmc":d['项目名称'],
                "xmdm":d['项目代码'],
                "xmdw":d['项目法人单位'],
                "xmtz":"",
                "xmzt":jieguo,
                "xmdz":"",
                "xmgk":"",
                "fabu_time":fabu_time
                }

    return json.dumps(result,ensure_ascii=False)

def ext_guangdongsheng(page,fabu_time,info=None):

    if page is None or page=='':
        return ''

    fabu_time=str(fabu_time)

    soup=BeautifulSoup(page,'html.parser')


    result,d={},{}
    d=collections.defaultdict(lambda :None)

    d.update(ext_tb1(str(soup.table)))

    result={

        "xmmc":d['项目名称'],
        "xmdm":d['备案项目编号'],
        "xmdw":"",
        "xmtz":d['项目总投资'],
        "xmzt":d['项目当前状态'],
        "xmdz":d['项目所在地'],
        "xmgk":d['项目规模及内容'],
        "fabu_time":fabu_time
        }
    return json.dumps(result,ensure_ascii=False)

def ext_beijingshi(page,fabu_time,info=None):
    if page is None or page=='':
        return ''
    fabu_time=str(fabu_time)

    if 'jieguo' in info:

        jieguo=json.loads(info)['jieguo']

    else:

        jieguo=''

    soup=BeautifulSoup(page,'html.parser')


    result={}

    d=collections.defaultdict(lambda :None)
    d.update(ext_tb1(str(soup.table)))

    result={

        "xmmc":d['项目名称'],
        "xmdm":d['项目代码'],
        "xmdw":d['申请单位'],
        "xmtz":"",
        "xmzt":jieguo,
        "xmdz":"",
        "xmgk":"",
        "fabu_time":fabu_time
        }

    return json.dumps(result,ensure_ascii=False)

def ext_anhuisheng(page,fabu_time,info=None):
    if page is None or page=='':
        return ''
    fabu_time=str(fabu_time)

    soup=BeautifulSoup(page,'html.parser')

    if 'jieguo' in info:

        jieguo=json.loads(info)['jieguo']

    else:

        jieguo=''

    result,d={},{}
    d=collections.defaultdict(lambda :None)

    d.update(ext_tb1(str(soup.table)))

    result={
                "xmmc":d['项目名称'],
                "xmdm":d['项目代码'],
                "xmdw":d['项目法人单位'],
                "xmtz":"",
                "xmzt":jieguo,
                "xmdz":"",
                "xmgk":"",
                "fabu_time":fabu_time
                }

    return json.dumps(result,ensure_ascii=False)






def ext_fujiansheng(page,fabu_time,info=None):
    fabu_time=str(fabu_time)
    soup=BeautifulSoup(page,'html.parser')

    result={}

    d1=ext_tb1(str(soup.find_all('table',attrs={"class":"zhuce_table_style txxx_table_style"})[0]))
    d=collections.defaultdict(lambda :None)

    d.update(d1)
    d1=d

    # xmdw=tbs[1].th.text.strip()
    span=soup.find_all('span',attrs={"name":'enterpristName'})
    if len(span)>0:
        xmdw=span[0].text.strip()
    else:
        xmdw=""
    tr=soup.find_all('tr',attrs={"class":"itemInfo"})
    if len(tr)>0:
        xmzt=tr[0].find_all('td')[-2].text.strip()
    else:
        xmzt=""
    result={
    "xmmc":d1['项目名称'],
    "xmdm":d1['项目编码'],
    "xmdw":xmdw,
    "xmtz":d1['项目总投资(万元)'],
    "xmzt":xmzt,
    "xmdz":d1['建设详细地址'],
    "xmgk":d1['主要建设内容及规模'],
    "fabu_time":fabu_time,
    }

    return json.dumps(result,ensure_ascii=False)



# 横向
def ext_tb1(table):
    soup=BeautifulSoup(table,'html.parser')

    trs=soup.find_all('tr')
    d={}
    for tr in trs:
        tds=tr.find_all('td')
        for i in range(int(len(tds)/2)):
            k,v=tds[2*i].text.strip(),tds[2*i+1].text.strip()
            d[k]=v
    return d

def ext_tb2(table):
    soup=BeautifulSoup(table,'html.parser')

    trs=soup.find_all('tr')
    txtarr=[  [td.text.strip() for td in tr.find_all('td')]  for tr in trs  ]
    d={}
    for i in range(int(len(txtarr)/2)):
        ks=txtarr[2*i]
        vs=txtarr[2*i+1]
        for k,v in zip(ks,vs):
            d[k]=v

    return d

