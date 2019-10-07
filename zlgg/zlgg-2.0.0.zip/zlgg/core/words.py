
from lmf.dbv2 import db_query
import os 
import copy  
import re 
def initwords_ol():
    df=db_query("select name,tag from v1.words",dbtype="postgresql",conp=["postgres","since2015","192.168.4.188","base","v1"])
    krr=df['name'].values.tolist()
    result={"xmmc":[],"zhaobiaoren":[],"zhongbiaoren":[],"kzj":[],"zhongbiaojia":[]
    ,"xmjl":[],"xmbh":[],"zbdl":[],"zbfs":[],"xmdz":[],"others":[]
    }
    a=df.to_dict(orient='records')
    for w in a:
        flag=0
        for k in result.keys():
                    if w['tag']==k:
                        result[k].append(w['name'])
                        flag=1
        if flag==0:result["others"].append(w['name'])
    datadict=result
    return krr,datadict 

def initwords_local():
    with open(os.path.join(os.path.dirname(__file__),'words.txt'),encoding='utf8') as f:
        lines=f.readlines()
    arr=[list( filter(lambda x:x.strip()!='',re.split('\s+',w))) for w in lines]

    krr=copy.deepcopy([w[0] for w in arr])

    result={"xmmc":[],"zhaobiaoren":[],"zhongbiaoren":[],"kzj":[],"zhongbiaojia":[]
    ,"xmjl":[],"xmbh":[],"zbdl":[],"zbfs":[],"xmdz":[],"others":[]
    }
    for w in arr:
        for k in result.keys():
                    if len(w)<=1:continue
                    if w[1]==k :
                        result[k].append(w[0])

    datadict=copy.deepcopy(result)
    return krr,datadict