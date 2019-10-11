#-*- coding:utf-8 -*-
import re
import json
import random
import time
import hashlib
import urllib
import requests
from bs4 import BeautifulSoup
from FortuneData.database import Company

data_url="https://fortune.com/global500/2019/search/"
json_data_url="https://content.fortune.com/wp-json/irving/v1/data/franchise-search-results"

def _get_fortune_data():
    data = None
    try:
        resp = requests.get(data_url)
        pat = r'\"identifier\":(\d+)'
        gp = re.search( pat, resp.text )
        if gp is not None:
            list_id = int(gp.groups()[0])
            resp = requests.get(json_data_url, params={"list_id":list_id} )
            data = resp.json()
    except Exception as e:
        raise Exception("Request Data Error!")
    finally:
        return _org_fortune_data( data )

def _org_fortune_data( data ):
    data_list=[]
    if data is not None:
        if data[1] is not None:
           for item in data[1].get("items"):
               fields = item.get("fields")
               data_item=[]
               for col in fields:
                   if col.get("key") == "rank":
                       data_item.append(col.get("value"))
                   if col.get("key") == "name":
                       data_item.insert(1,col.get("value"))
                   if col.get("key") == "revenues":
                       data_item.append(col.get("value"))
                   if col.get("key") == "profits":
                       data_item.append(col.get("value"))
                   if col.get("key") == "assets":
                       data_item.append(col.get("value"))
                   if col.get("key") == "employees":
                       data_item.append(col.get("value"))
               data_list.append(data_item)
        return sorted(data_list, key=lambda x:int(x[0]), reverse=True )

def load_fortune_data(appid=None, secretKey=None):
    '''加载财富网站世界500强数据，默认不翻译
    appid 百度翻译开放平台appid
    secretKey 百度翻译开放平台密钥
    '''
    data = _get_fortune_data()
    for item in data:
        p = Company.select().where(Company.en_name == item[1] )
        if p.count() == 0:
            cn_name = ''
            if appid is not None and secretKey is not None:
                #获取中文翻译
                cn_name = get_company_cn_name( item[1], appid, secretKey )
                time.sleep(1)
            p = Company( en_name=item[1], cn_name=cn_name, rank=item[0], revenues=item[2], profits=item[3], assets=item[4], employees=item[5] )
            p.save()
        else:
            pp = p.get()
            if pp.cn_name == '' or pp.cn_name is None:
                if appid is not None and secretKey is not None:
                    cn_name = get_company_cn_name(item[1], appid, secretKey)
                    time.sleep(1)
                    pp.cn_name=cn_name
                    pp.save()

def get_company_cn_name( en_name, appid, secretKey ):
    '''
    从百度翻译平台获取翻译后的中文
    en_name 英文
    appid 百度翻译开放平台appid
    secretKey 百度翻译开放平台密钥
    返回翻译后的中文
    '''
    cn_name=''
    myurl="http://api.fanyi.baidu.com/api/trans/vip/translate"
    appid=appid
    secretKey=secretKey
    fromLang = "en"
    toLang = "zh"
    salt = random.randint(32768,65536)
    q = en_name
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    request_url = myurl + "?appid=" + appid + "&q=" + urllib.parse.quote(q) + "&from=" + fromLang + "&to=" + toLang + "&salt=" + str(salt) + "&sign=" + sign
    try:
        resp = requests.get( request_url )
        result =  resp.json()
        if result:
            ret = result.get("trans_result")
            if len(ret) > 0:
                cn_name = ret[0].get("dst")
        else:
            print("not return data!")
    except Exception as e:
        print(e)
    finally:
        return cn_name

if __name__ == '__main__':
    load_fortune_data()
