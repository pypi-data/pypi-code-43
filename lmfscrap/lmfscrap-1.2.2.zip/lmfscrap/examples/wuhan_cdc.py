
import pandas as pd  
import re 
from selenium import webdriver 
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 


from   lmfscrap import web
__conp=["postgres","since2015","192.168.3.171","scrapy4","wuhan"]

def f1(driver,num):


    locator=(By.XPATH,"//tr[contains(@id,'datagrid-row')]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    locator=(By.CLASS_NAME,"pagination-num")
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    val=driver.find_element_by_class_name("pagination-num").get_attribute("value")
    if int(val)!=num:
        text1=driver.find_element_by_xpath("//tr[@id='datagrid-row-r1-1-0']/td[1]").text



        locator=(By.CLASS_NAME,"pagination-num")
        WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
        input=driver.find_element_by_class_name("pagination-num")
        input.clear()
        input.send_keys(num)

        input.send_keys(Keys.ENTER)
        locator=(By.XPATH,"//tr[contains(@id,'datagrid-row')]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        locator=(By.XPATH,"//tr[@id='datagrid-row-r1-1-0']/td[1][string()!='%s']"%text1)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))


    page=driver.page_source
    soup=BeautifulSoup(page,'lxml')

    tbs=soup.find_all("table",class_="datagrid-btable")
    data=[]
    for tb in tbs:
        tmp=[]
        trs=tb.find_all("tr")
        for tr in trs:
            tds=tr.find_all("td")
            arr=[ td.text.strip() for td in tds]
            a=tr.find('a')
            if a is not None:
                lk=re.findall("'([^']*)'",a["onclick"])[0]
                #pre_url='/'.join(driver.current_url.split("/")[:3])
                lk="http://www.jy.whzbtb.com/V2PRTS/"+lk
                arr.append(lk)
            tmp.append(arr)
        data.append(tmp)
    data1=[w1+w2 for w1,w2 in zip(*data)]
    df=pd.DataFrame(data=data1)
    df=df[df.columns[1:]]
    return df



def f2(driver):
     locator=(By.ID,"datagrid-row-r1-1-0")

     WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))

     x=driver.find_elements_by_xpath("//div[@class='datagrid-pager pagination']/table/tbody/tr/td/span")[1].text
     total=int(x[1:-1])
     return total

def zhaobiao(conp,total=5):
    url="""http://www.jy.whzbtb.com/V2PRTS/TendererNoticeInfoListInit.do"""
    col=["name","status","href","bh","zbr","ggstart_time","ggend_time","zczj","laiyuan","pbbanfa"]
    tb="zhaobiao_gg_cdc"
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#1 招标公告
def zhaobiao_gg(total):
    url="""http://www.jy.whzbtb.com/V2PRTS/TendererNoticeInfoListInit.do"""
    col=["name","status","href","bh","zbr","ggstart_time","ggend_time","zczj","laiyuan","pbbanfa"]
    tb="zhaobiao_gg_cdc"
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

def zhaobiao_gg_test(total):
    url="""http://www.jy.whzbtb.com/V2PRTS/TendererNoticeInfoListInit.do"""
    col=["name","status","href","bh","zbr","ggstart_time","ggend_time","zczj","laiyuan","pbbanfa"]
    tb="zhaobiao_gg_cdc_test"
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":2,
    "total":total
    }
    m=web()
    m.write(**setting)


#2 变更公告
def biangen_gg(total):
    url="http://www.jy.whzbtb.com/V2PRTS/AmendBulletinInfoListInit.do"
    col=["name","status","href","ggstart_time","yuangg_bh"]

    tb='biangen_gg_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)


#3 中标结果公示
# url="http://www.jy.whzbtb.com/V2PRTS/WinBidBulletinInfoListInit.do"
# col=["name","biaoduanxuhao","zhongbiaoren","zhongbiaojia","href","zhongbiaobh","jsdw","dailidw"]


def zhongbiaojieguo_gs(total):
    url="http://www.jy.whzbtb.com/V2PRTS/WinBidBulletinInfoListInit.do"
    col=["name","biaoduanxuhao","zhongbiaoren","zhongbiaojia","href","zhongbiaobh","jsdw","dailidw"]
    tb="zhongbiaojieguo_gs_cdc"
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#4 放弃中标公告
# url="http://www.jy.whzbtb.com/V2PRTS/AbandonNoticeInfoListInit.do"
# col=["name","href","biaoduanxuhao","fqdw","ggstart_time","ggstatus"]

def fangqizhongbiao_gs(total):
    url="http://www.jy.whzbtb.com/V2PRTS/AbandonNoticeInfoListInit.do"
    col=["name","href","biaoduanxuhao","fqdw","ggstart_time","ggstatus"]
    tb="fangqizhongbiao_gs_cdc"
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,

    "total":total
    }
    m=web()
    m.write(**setting)

#5 开标安排
# url="http://www.jy.whzbtb.com/V2PRTS/OpeningReserveInfoListInit.do"
# col=["ggstart_time","name","href","biaoduanxuhao","leixing","kb_didian","kb_shi","pb_shi","jy_leibie","zb_leibie","jiandudanwei","total_tbr","zhaobiaoren"]

def kbanpai(total):
    url="http://www.jy.whzbtb.com/V2PRTS/OpeningReserveInfoListInit.do"
    col=["ggstart_time","name","href","biaoduanxuhao","leixing","kb_didian","kb_shi","pb_shi","jy_leibie","zb_leibie","jiandudanwei","total_tbr","zhaobiaoren"]
    tb='kbanpai_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#6 招标项目登记
# url="http://www.jy.whzbtb.com/V2PRTS/ConstructionInfoListInit.do"
# col=["name","href","baojiandanwei","xmwh","gclx","baojian_xz","pizhun_touzi"]
def xmdj(total):
    url="http://www.jy.whzbtb.com/V2PRTS/OpeningReserveInfoListInit.do"
    col=["ggstart_time","name","href","biaoduanxuhao","leixing","kb_didian","kb_shi","pb_shi","jy_leibie","zb_leibie","jiandudanwei","total_tbr","zhaobiaoren"]
    tb='xmdj_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#7 资格预审结果公示
# url="http://www.jy.whzbtb.com/V2PRTS/PrequalificationPublicityInfoListInit.do"
# col=["name","ysdw","href","zbgg","djbh","ysstart_time","ysend_time","chouqian_time","chouqian_didian"]
def zgys_gs(total):
    url="http://www.jy.whzbtb.com/V2PRTS/PrequalificationPublicityInfoListInit.do"
    col=["name","ysdw","href","zbgg","djbh","ysstart_time","ysend_time","chouqian_time","chouqian_didian"]
    tb='zgys_gs_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)



#8 中标公示
def zhongbiao_gs(total):
    url="http://www.jy.whzbtb.com/V2PRTS/WinningPublicityInfoListInit.do"
    col=["name","href","biaoduanxuhao","zblr","zbfangshi","zhongbiaoren","zhongbiaojia","ggend_time"]
    tb='zhongbiao_gs_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total

    }
    m=web()
    m.write(**setting)

#9 发包备案公示
#url="http://www.jy.whzbtb.com/V2PRTS/ContractRecordDirectlyInfoListInit.do"
#col=["name","href","jiandubumen","bjbh","jsdw","pizhunwh","sigongdw",'jihuagq',"gczhaojia"]

def fabao_gs(total):
    url="http://www.jy.whzbtb.com/V2PRTS/ContractRecordDirectlyInfoListInit.do"
    col=["name","href","jiandubumen","bjbh","jsdw","pizhunwh","sigongdw",'jihuagq',"gczhaojia"]
    tb='fabao_gs_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#10 资格预审澄清
# url="http://www.jy.whzbtb.com/V2PRTS/PrequalificationClarifyInfoListInit.do"
# col=["name","href","zblb","yswj","zbfangshi","zhaobiaoren"]

def zgys_chqing(total):
    url="http://www.jy.whzbtb.com/V2PRTS/PrequalificationClarifyInfoListInit.do"
    col=["name","href","zblb","yswj","zbfangshi","zhaobiaoren"]
    tb='zgys_chqing_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#11 招标文件澄清
# url="http://www.jy.whzbtb.com/V2PRTS/UnbidDocumentsClarifyInfoListInit.do"
# col=["name","biaoduanxuhao","href","bjbh","zbdjbh","zbbh","xmzbdw","zblb","zbfangshi","zbdaili"] 

def zbwj_chqing(total):
    url="http://www.jy.whzbtb.com/V2PRTS/UnbidDocumentsClarifyInfoListInit.do"
    col=["name","biaoduanxuhao","href","bjbh","zbdjbh","zbbh","xmzbdw","zblb","zbfangshi","zbdaili"] 
    tb='zbwj_chqing_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#12 控制价公示
# url="http://www.jy.whzbtb.com/V2PRTS/ControlPriceListInit.do"
# col=["name","href","zbggbh","zhaobiaoren","ggstart_time","ggend_time"]

def kzj_gs(total):
    url="http://www.jy.whzbtb.com/V2PRTS/ControlPriceListInit.do"
    col=["name","href","zbggbh","zhaobiaoren","ggstart_time","ggend_time"]
    tb='kzj_gs_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#13 招标异常报告
# url="http://www.jy.whzbtb.com/V2PRTS/TenderAbnormalReportInfoListInit.do"
# col=["name","href","status","zhaobiaoren","zbdaili","jianguanbumen"]

def zbyichang(total):
    url="http://www.jy.whzbtb.com/V2PRTS/TenderAbnormalReportInfoListInit.do"
    col=["name","href","status","zhaobiaoren","zbdaili","jianguanbumen"]
    tb='zbyichang_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#14 招标人信息
# url="http://www.jy.whzbtb.com/V2PRTS/TendereeInfoListInit.do"
# col=["name","cn"]

def zbr_xx(total):
    url="http://www.jy.whzbtb.com/V2PRTS/TendereeInfoListInit.do"
    col=["name","cn"]
    tb='zbr_xx_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#15 投标人信息
# url="http://www.jy.whzbtb.com/V2PRTS/TendererInfoListInit.do"
# col=["name","cn"]
def tbr_xx(total):
    url="http://www.jy.whzbtb.com/V2PRTS/TendererInfoListInit.do"
    col=["name","cn"]
    tb='tbr_xx_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)


#16 交易人信息
# url="http://www.jy.whzbtb.com/V2PRTS/CorpInfoListInit.do"
# col=["name","href","gslx","zhuce_time","zhuce_zj"]
def jyr_xx(total):
    url="http://www.jy.whzbtb.com/V2PRTS/CorpInfoListInit.do"
    col=["name","href","gslx","zhuce_time","zhuce_zj"]
    tb='jyr_xx_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#17 注册人员信息
# url="http://www.jy.whzbtb.com/V2PRTS/RegPersonInfoListInit.do"
# col=["name","dwmc","gender","xueli","leixing","dj","zhuanye","bh","youxiaoqi"]
def zhuceren_xx(total):
    url="http://www.jy.whzbtb.com/V2PRTS/RegPersonInfoListInit.do"
    col=["name","dwmc","gender","xueli","leixing","dj","zhuanye","bh","youxiaoqi"]
    tb='zhuceren_xx_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20,
    "total":total
    }
    m=web()
    m.write(**setting)


#18 交易人业绩信息
# url="http://www.jy.whzbtb.com/V2PRTS/AchievementInfoListInit.do"
# col=["name","href","dwmc","zblb","zhongbiao_time","zhongbiaojia"]

def jyr_yejixx(total):
    url="http://www.jy.whzbtb.com/V2PRTS/AchievementInfoListInit.do"
    col=["name","href","dwmc","zblb","zhongbiao_time","zhongbiaojia"]
    tb='jyr_yejixx_cdc'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)

#19 招标代理信息
# url="http://www.jy.whzbtb.com/V2PRTS/BiddingAgencyListInit.do"
# col=["name","href","gclx","zhuce_time","zhuce_zijin"]

def dailiren_xx(total):
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)


#20 开标记录
# url="http://www.jy.whzbtb.com/V2PRTS/BidOpeningRecordInfoListInit.do"
# col=["name","href","kb_shi","kb_time","kb_leixing","is_dianzi"]
def kbjl(total):
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4,
    "total":total
    }
    m=web()
    m.write(**setting)



def work_cdc():
    total=20
    try:
        zhaobiao_gg(total)
    except:
        print("zhaobiao_gg失败")

    try:
        biangen_gg(total)
    except:
        print("biangen_gg 失败")

    try:
        zhongbiaojieguo_gs(total)
    except:
        print("zhongbiaojieguo_gs 失败")

    try:
        fangqizhongbiao_gs(total)
    except:
        print("fangqizhongbiao_gs 失败")
    try:
        kbanpai(total)
    except:
        print("kbanpai 失败")
    try:
        xmdj(total)
    except:
        print("xmdj 失败")
    try:
        zgys_gs(total)
    except:
        print("zgys_gs 失败")
    try:

        zhongbiao_gs(total)
    except:
        print("zhongbiao_gs 失败")

    try:
        fabao_gs(total)
    except:
        print("fabao_gs 失败")

    try:
        zgys_chqing(total)
    except:
        print("zgys_chqing 失败")

    try:
        zbwj_chqing(total)
    except:
        print("zbwj_chqing 失败")
    try:
        kzj_gs(total)
    except:
        print("kzj_gs 失败")

    try:
        zbyichang(total)
    except:
        print("zbyichang 失败")

    try:
        zbr_xx(total)
    except:
        print("zbr_xx 失败")

    try:

        tbr_xx(total)
    except:
        print("tbr_xx 失败")

    try:
        jyr_xx(total)
    except:
        print("jyr_xx")

    try:
        zhuceren_xx(total)
    except:
        print("zhuren_xx")

    try:
        jyr_yejixx(total)
    except:
        print("jyr_jyjixx")

def cdc_general(tb):
    sql="""
    insert into wuhan.%s

    select * from wuhan.%s_cdc

    except 

    select * from wuhan.%s
    """%(tb,tb,tb)

    db_command(sql,dbtype="postgresql",conp=__conp)


def cdc():
    for tb in ["zhongbiao_gs","zhongbiaojieguo_gs","zhongbiao_gs","biangen_gg","kzj_gs"]:
        cdc_general(tb)
