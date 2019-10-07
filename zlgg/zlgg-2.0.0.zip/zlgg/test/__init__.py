from lmf.dbv2 import db_query 
from bs4 import BeautifulSoup
import selenium 
# from lmfgg.table.tbpre import get_pure_tbs 

# from lmfgg.getdata import extpage_ol
from zlgg.clear import *

import sys 

from selenium import webdriver
import os 
import json


def wp(page):
    with open(sys.path[0]+"\\test.html",'w',encoding='utf8') as f :
        f.write(page)

def getpage(href,quyu):
    conp=["gpadmin","since2015","192.168.4.179","base_db","bid"]
    tb="b_%s"%quyu
    #href="""http://58.222.225.18/ggzy/InfoDetail/Default.aspx?InfoID=14d96376-8dba-4fa0-a380-ad890ac9fd97&CategoryNum=004001001"""
    df=db_query("select * from bid.%s where href= '%s' "%(tb,href),dbtype="postgresql",conp=conp)

    page=df.at[0,'page']

    return page 


page=getpage("http://ggj.chizhou.gov.cn/chiztpfront/ztbdetail/ztbjsdetail.aspx?type=2&InfoID=37ad5312-898b-4203-9428-9f50790042e5&CategoryNum=002001002001","anhui_chizhou")

wp(page)

# soup=BeautifulSoup(page,'lxml')


# trs=soup.find_all('tr')





