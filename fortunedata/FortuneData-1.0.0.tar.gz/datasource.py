#-*- coding:utf-8 -*-
import re
import json
import random
import time
import hashlib
import urllib
import requests
from bs4 import BeautifulSoup
from database import Company

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

def load_fortune_data(appid, secretKey):
    data = _get_fortune_data()
    for item in data:
        p = Company.select().where(Company.en_name == item[1] )
        print("count:%d en_name:%s"%(p.count(),item[1]))
        if p.count() == 0:
            cn_name = get_company_cn_name( item[1], appid, secretKey )
            p = Company( en_name=item[1], rank=item[0], revenues=item[2], profits=item[3], assets=item[4], employees=item[5] )
            p.save()
        else:
            pp = p.get()
            if pp.cn_name == '' or pp.cn_name is None:
                cn_name = get_company_cn_name(item[1], appid, secretKey)
                time.sleep(1)
                print(cn_name)
                pp.cn_name=cn_name
                pp.save()

def get_company_cn_name( en_name, appid, secretKey ):
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
