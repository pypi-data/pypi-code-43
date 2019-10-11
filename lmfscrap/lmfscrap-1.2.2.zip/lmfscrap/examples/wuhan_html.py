import pandas as pd  
import re 

from selenium import webdriver 
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_query
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 


from lmfscrap import page
import time 

def f(driver,url):


    driver.get(url)

    locator=(By.CLASS_NAME,"trading_publicly_fr")

    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))

    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break

    page=driver.page_source

    soup=BeautifulSoup(page,'lxml')

    div=soup.find_all('div',class_='trading_publicly_fr')[0]
    return div

def html_template(tb,size=None):
    m=page()
    if size is not None:
        sql="select href from wuhan.%s limit %d"%(tb,size) 
    else :
        sql="select href from wuhan.%s "%tb 

    conp=["postgres","since2015","192.168.3.171","scrapy4","wuhan"]
    df=db_query(sql,dbtype="postgresql",conp=conp)
    arr=df["href"].values



    setting={"num":20,"arr":arr,"f":f,"conp":conp,"tb":"%s_html"%tb}
    m.write(**setting)

def bujiu(tb):
    m=page()
    sql="select href from wuhan.%s where href not in(select href from wuhan.%s_html)"%(tb,tb)
    conp=["postgres","since2015","192.168.3.171","scrapy4","wuhan"]
    df=db_query(sql,dbtype="postgresql",conp=conp)
    arr=df["href"].values

    setting={"num":20,"arr":arr,"f":f,"conp":conp,"tb":"%s_html"%tb}
    m.write(**setting)
# for tb in ["zhaobiao_gg","zhongbiao_gs","zhongbiaojieguo_gs"]:
#     html_template(tb)

#html_template("zhongbiao_gs")
#bujiu("zhongbiao_gs")

#html_template("zhongbiaojieguo_gs")
#bujiu("zhongbiaojieguo_gs")
def work():
    for tb in ["zhaobiao_gg","zhongbiao_gs","zhongbiaojieguo_gs","biangen_gg","kzj_gs","fangqizhongbiao_gs"]:
        html_template(tb)
        bujiu(tb)





def template(tb,conp,size=None):
    m=page()
    if size is not None:
        sql="select href from %s.%s limit %d"%(conp[4],tb,size) 
    else :
        sql="select href from %s.%s "%(conp[4],tb) 

    
    df=db_query(sql,dbtype="postgresql",conp=conp)
    arr=df["href"].values

    setting={"num":20,"arr":arr,"f":f,"conp":conp,"tb":"%s_html"%tb}
    m.write(**setting)


