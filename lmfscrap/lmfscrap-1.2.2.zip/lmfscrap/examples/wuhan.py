import pandas as pd  
import re 

from selenium import webdriver 
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 



from  lmfscrap import web 

#招标公告
#url="""http://www.jy.whzbtb.com/V2PRTS/TendererNoticeInfoListInit.do"""
#变更公告
#url="http://www.jy.whzbtb.com/V2PRTS/AmendBulletinInfoListInit.do"
#中标结果公示
#url="http://www.jy.whzbtb.com/V2PRTS/WinBidBulletinInfoListInit.do"

#放弃中标公告
#url="http://www.jy.whzbtb.com/V2PRTS/AbandonNoticeInfoListInit.do"

#开标安排
#url="http://www.jy.whzbtb.com/V2PRTS/OpeningReserveInfoListInit.do"

#招标项目登记
#url="http://www.jy.whzbtb.com/V2PRTS/ConstructionInfoListInit.do"

#资格预审结果公示
#url="http://www.jy.whzbtb.com/V2PRTS/PrequalificationPublicityInfoListInit.do"

#中标公示
#url="http://www.jy.whzbtb.com/V2PRTS/WinningPublicityInfoListInit.do"

#发包备案公示
#url="http://www.jy.whzbtb.com/V2PRTS/ContractRecordDirectlyInfoListInit.do"

#资格预审澄清
#url="http://www.jy.whzbtb.com/V2PRTS/PrequalificationClarifyInfoListInit.do"

#招标文件澄清
#url="http://www.jy.whzbtb.com/V2PRTS/UnbidDocumentsClarifyInfoListInit.do"

#控制价公示
#url="http://www.jy.whzbtb.com/V2PRTS/ControlPriceListInit.do"

#招标异常报告
#url="http://www.jy.whzbtb.com/V2PRTS/TenderAbnormalReportInfoListInit.do"

#招标人信息
#url="http://www.jy.whzbtb.com/V2PRTS/TendereeInfoListInit.do"

#投标人信息
#url="http://www.jy.whzbtb.com/V2PRTS/TendererInfoListInit.do"

#交易人信息
#url="http://www.jy.whzbtb.com/V2PRTS/CorpInfoListInit.do"

#注册人员信息
#url="http://www.jy.whzbtb.com/V2PRTS/RegPersonInfoListInit.do"

#交易人业绩信息
#url="http://www.jy.whzbtb.com/V2PRTS/AchievementInfoListInit.do"

#招标代理信息
#url="http://www.jy.whzbtb.com/V2PRTS/BiddingAgencyListInit.do"

#远程异地评标
#url="http://www.jy.whzbtb.com/V2PRTS/RemoteBidEvaluationInfoListInit.do"

#开标记录
#url="http://www.jy.whzbtb.com/V2PRTS/BidOpeningRecordInfoListInit.do"

#评标报告概述
#url="http://www.jy.whzbtb.com/V2PRTS/EvaluationReportInfoListInit.do"

#中标金额排行
#url="http://www.jy.whzbtb.com/V2PRTS/ProjectWinningRateListInit.do"


#注册人异动
#url="http://www.jy.whzbtb.com/V2PRTS/PersonModifyinfoInfoListInit.do"

# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

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


def zhaobiao(conp):
    url="""http://www.jy.whzbtb.com/V2PRTS/TendererNoticeInfoListInit.do"""
    col=["name","status","href","bh","zbr","ggstart_time","ggend_time","zczj","laiyuan","pbbanfa"]
    tb="zhaobaio"
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":conp,
    "num":10,


    }
    m=web()
    m.write(**setting)

#招标公告
def zhaobiao_gg():
    url="""http://www.jy.whzbtb.com/V2PRTS/TendererNoticeInfoListInit.do"""
    col=["name","status","href","bh","zbr","ggstart_time","ggend_time","zczj","laiyuan","pbbanfa"]
    tb="zhaobaio_gg"
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":10,


    }
    m=web()
    m.write(**setting)


#变更公告
def biangen_gg():
    url="http://www.jy.whzbtb.com/V2PRTS/AmendBulletinInfoListInit.do"
    col=["name","status","href","ggstart_time","yuangg_bh"]

    tb='biangen_gg'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":4
    }
    m=web()
    m.write(**setting)


#中标结果公示
# url="http://www.jy.whzbtb.com/V2PRTS/WinBidBulletinInfoListInit.do"
# col=["name","biaoduanxuhao","zhongbiaoren","zhongbiaojia","href","zhongbiaobh","jsdw","dailidw"]


def zhongbiaojieguo_gs():
    url="http://www.jy.whzbtb.com/V2PRTS/WinBidBulletinInfoListInit.do"
    col=["name","biaoduanxuhao","zhongbiaoren","zhongbiaojia","href","zhongbiaobh","jsdw","dailidw"]
    tb="zhongbiaojieguo_gs"
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":10
    }
    m=web()
    m.write(**setting)

#放弃中标公告
# url="http://www.jy.whzbtb.com/V2PRTS/AbandonNoticeInfoListInit.do"
# col=["name","href","biaoduanxuhao","fqdw","ggstart_time","ggstatus"]

def fangqizhongbiao_gs():
    url="http://www.jy.whzbtb.com/V2PRTS/AbandonNoticeInfoListInit.do"
    col=["name","href","biaoduanxuhao","fqdw","ggstart_time","ggstatus"]
    tb="fangqizhongbiao_gs"
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":10
    }
    m=web()
    m.write(**setting)

#开标安排
# url="http://www.jy.whzbtb.com/V2PRTS/OpeningReserveInfoListInit.do"
# col=["ggstart_time","name","href","biaoduanxuhao","leixing","kb_didian","kb_shi","pb_shi","jy_leibie","zb_leibie","jiandudanwei","total_tbr","zhaobiaoren"]

def kbanpai():
    url="http://www.jy.whzbtb.com/V2PRTS/OpeningReserveInfoListInit.do"
    col=["ggstart_time","name","href","biaoduanxuhao","leixing","kb_didian","kb_shi","pb_shi","jy_leibie","zb_leibie","jiandudanwei","total_tbr","zhaobiaoren"]
    tb='kbanpai'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":10
    }
    m=web()
    m.write(**setting)

#招标项目登记
# url="http://www.jy.whzbtb.com/V2PRTS/ConstructionInfoListInit.do"
# col=["name","href","baojiandanwei","xmwh","gclx","baojian_xz","pizhun_touzi"]
def xmdj():
    url="http://www.jy.whzbtb.com/V2PRTS/OpeningReserveInfoListInit.do"
    col=["ggstart_time","name","href","biaoduanxuhao","leixing","kb_didian","kb_shi","pb_shi","jy_leibie","zb_leibie","jiandudanwei","total_tbr","zhaobiaoren"]
    tb='xmdj'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":10
    }
    m=web()
    m.write(**setting)

#资格预审结果公示
# url="http://www.jy.whzbtb.com/V2PRTS/PrequalificationPublicityInfoListInit.do"
# col=["name","ysdw","href","zbgg","djbh","ysstart_time","ysend_time","chouqian_time","chouqian_didian"]
def zgys_gs():
    url="http://www.jy.whzbtb.com/V2PRTS/PrequalificationPublicityInfoListInit.do"
    col=["name","ysdw","href","zbgg","djbh","ysstart_time","ysend_time","chouqian_time","chouqian_didian"]
    tb='zgys_gs'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":10
    }
    m=web()
    m.write(**setting)



#中标公示
def zhongbiao_gs():
    url="http://www.jy.whzbtb.com/V2PRTS/WinningPublicityInfoListInit.do"
    col=["name","href","biaoduanxuhao","zblr","zbfangshi","zhongbiaoren","zhongbiaojia","ggend_time"]
    tb='zhongbiao_gs'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":10,

    }
    m=web()
    m.write(**setting)

#发包备案公示
#url="http://www.jy.whzbtb.com/V2PRTS/ContractRecordDirectlyInfoListInit.do"
#col=["name","href","jiandubumen","bjbh","jsdw","pizhunwh","sigongdw",'jihuagq',"gczhaojia"]

def fabao_gs():
    url="http://www.jy.whzbtb.com/V2PRTS/ContractRecordDirectlyInfoListInit.do"
    col=["name","href","jiandubumen","bjbh","jsdw","pizhunwh","sigongdw",'jihuagq',"gczhaojia"]
    tb='fabao_gs'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)

#资格预审澄清
# url="http://www.jy.whzbtb.com/V2PRTS/PrequalificationClarifyInfoListInit.do"
# col=["name","href","zblb","yswj","zbfangshi","zhaobiaoren"]

def zgys_chqing():
    url="http://www.jy.whzbtb.com/V2PRTS/PrequalificationClarifyInfoListInit.do"
    col=["name","href","zblb","yswj","zbfangshi","zhaobiaoren"]
    tb='zgys_chqing'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)

#招标文件澄清
# url="http://www.jy.whzbtb.com/V2PRTS/UnbidDocumentsClarifyInfoListInit.do"
# col=["name","biaoduanxuhao","href","bjbh","zbdjbh","zbbh","xmzbdw","zblb","zbfangshi","zbdaili"] 

def zbwj_chqing():
    url="http://www.jy.whzbtb.com/V2PRTS/UnbidDocumentsClarifyInfoListInit.do"
    col=["name","biaoduanxuhao","href","bjbh","zbdjbh","zbbh","xmzbdw","zblb","zbfangshi","zbdaili"] 
    tb='zbwj_chqing'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)

#控制价公示
# url="http://www.jy.whzbtb.com/V2PRTS/ControlPriceListInit.do"
# col=["name","href","zbggbh","zhaobiaoren","ggstart_time","ggend_time"]

def kzj_gs():
    url="http://www.jy.whzbtb.com/V2PRTS/ControlPriceListInit.do"
    col=["name","href","zbggbh","zhaobiaoren","ggstart_time","ggend_time"]
    tb='kzj_gs'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)

#招标异常报告
# url="http://www.jy.whzbtb.com/V2PRTS/TenderAbnormalReportInfoListInit.do"
# col=["name","href","status","zhaobiaoren","zbdaili","jianguanbumen"]

def zbyichang():
    url="http://www.jy.whzbtb.com/V2PRTS/TenderAbnormalReportInfoListInit.do"
    col=["name","href","status","zhaobiaoren","zbdaili","jianguanbumen"]
    tb='zbyichang'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)

#招标人信息
# url="http://www.jy.whzbtb.com/V2PRTS/TendereeInfoListInit.do"
# col=["name","cn"]

def zbr_xx():
    url="http://www.jy.whzbtb.com/V2PRTS/TendereeInfoListInit.do"
    col=["name","cn"]
    tb='zbr_xx'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)

#投标人信息
# url="http://www.jy.whzbtb.com/V2PRTS/TendererInfoListInit.do"
# col=["name","cn"]
def tbr_xx():
    url="http://www.jy.whzbtb.com/V2PRTS/TendererInfoListInit.do"
    col=["name","cn"]
    tb='tbr_xx'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)


#交易人信息
# url="http://www.jy.whzbtb.com/V2PRTS/CorpInfoListInit.do"
# col=["name","href","gslx","zhuce_time","zhuce_zj"]
def jyr_xx():
    url="http://www.jy.whzbtb.com/V2PRTS/CorpInfoListInit.do"
    col=["name","href","gslx","zhuce_time","zhuce_zj"]
    tb='jyr_xx'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)

#注册人员信息
# url="http://www.jy.whzbtb.com/V2PRTS/RegPersonInfoListInit.do"
# col=["name","dwmc","gender","xueli","leixing","dj","zhuanye","bh","youxiaoqi"]
def zhuceren_xx():
    url="http://www.jy.whzbtb.com/V2PRTS/RegPersonInfoListInit.do"
    col=["name","dwmc","gender","xueli","leixing","dj","zhuanye","bh","youxiaoqi"]
    tb='zhuceren_xx'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)


#交易人业绩信息
# url="http://www.jy.whzbtb.com/V2PRTS/AchievementInfoListInit.do"
# col=["name","href","dwmc","zblb","zhongbiao_time","zhongbiaojia"]

def jyr_yejixx():
    url="http://www.jy.whzbtb.com/V2PRTS/AchievementInfoListInit.do"
    col=["name","href","dwmc","zblb","zhongbiao_time","zhongbiaojia"]
    tb='jyr_yejixx'
    
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)

#招标代理信息
# url="http://www.jy.whzbtb.com/V2PRTS/BiddingAgencyListInit.do"
# col=["name","href","gclx","zhuce_time","zhuce_zijin"]

def dailiren_xx():
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)


#开标记录
# url="http://www.jy.whzbtb.com/V2PRTS/BidOpeningRecordInfoListInit.do"
# col=["name","href","kb_shi","kb_time","kb_leixing","is_dianzi"]
def kbjl():
    setting={
    "url":url,
    "f1":f1,
    "f2":f2,
    "tb":tb,
    "col":col,
    "conp":__conp,
    "num":20
    }
    m=web()
    m.write(**setting)



def work():
    try:
        zhaobiao_gg()
    except:
        print("zhaobiao_gg失败")

    try:
        biangen_gg()
    except:
        print("biangen_gg 失败")

    try:
        zhongbiaojieguo_gs()
    except:
        print("zhongbiaojieguo_gs 失败")

    try:
        fangqizhongbiao_gs()
    except:
        print("fangqizhongbiao_gs 失败")
    try:
        kbanpai()
    except:
        print("kbanpai 失败")
    try:
        xmdj()
    except:
        print("xmdj 失败")
    try:
        zgys_gs()
    except:
        print("zgys_gs 失败")
    try:

        zhongbiao_gs()
    except:
        print("zhongbiao_gs 失败")

    try:
        fabao_gs()
    except:
        print("fabao_gs 失败")

    try:
        zgys_chqing()
    except:
        print("zgys_chqing 失败")

    try:
        zbwj_chqing()
    except:
        print("zbwj_chqing 失败")
    try:
        kzj_gs()
    except:
        print("kzj_gs 失败")

    try:
        zbyichang()
    except:
        print("zbyichang 失败")

    try:
        zbr_xx()
    except:
        print("zbr_xx 失败")

    try:

        tbr_xx()
    except:
        print("tbr_xx 失败")

    try:
        jyr_xx()
    except:
        print("jyr_xx")

    try:
        zhuceren_xx()
    except:
        print("zhuren_xx")

    try:
        jyr_yejixx()
    except:
        print("jyr_jyjixx")

    # try:
    #     dailiren_xx()
    # except:
    #     print("dailiren_xx")

    # try:
    #     kbjl()
    # except:
    #     print("kbjl")


