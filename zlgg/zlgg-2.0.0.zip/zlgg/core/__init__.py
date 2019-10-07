#core模块负责基本的条件判断

#这里处理的前提是 A IS B 

from bs4 import BeautifulSoup
from lmf.dbv2 import db_query
import re
import Levenshtein

#看某个词是否和exm集合中的词匹配
def ismat(word,exm):

    word=re.sub("[^\u4E00-\u9FA5]",'',word)
    for w in exm:
        if Levenshtein.ratio(w,word)>=0.86:
            return True 
    return False

#看k匹配了那个词
def matwhat(k,krrdict):
    for w in krrdict.keys():
        if ismat(k,krrdict[w]):
            return w 
    return k

#看一组词是否匹配

######
def fismat(exm,arr,ng=3):
    k=ng
    for i in range(len(arr)):
        for j in range(k):
            word=''.join(arr[i:i+j+1])

            if ismat(word,exm):
                #print(word)
                return 1
    return 0


def cismat(hwd,arr):
    count=0
    for wd in hwd:
        count+=fismat(wd,arr)
    return count

######

def getpage(url,quyu):
    sql="select * from v3.t_gg where quyu='%s' and href='%s' "%(quyu,url)

    conp=['gpadmin','since2015','192.168.4.179','base_db','v3']
    df=db_query(sql,dbtype="postgresql",conp=conp)
 
    if not df.empty:
        page=df.at[0,'page']
        return page 
    return None

#文本分割算法
def to_arr(page):
    cm=["：","：","。"]
    if page is None:return []
    soup=BeautifulSoup(page,'lxml')
    tmp=soup.find('style')
    if tmp is not  None:tmp.clear()
    tmp=soup.find('script')
    if tmp is not  None:tmp.clear()
    arr=[]
    for w in soup.strings:
    #for w in soup.get_text('$lmf$lmf$').split("$lmf$lmf$")
            w=w.strip()
            if w=='':continue
            if len(w)==1 and w not in cm:continue
            x=re.split("[\s;；\xa0]{2,}",w)
            arr.extend(x)
    return arr 






