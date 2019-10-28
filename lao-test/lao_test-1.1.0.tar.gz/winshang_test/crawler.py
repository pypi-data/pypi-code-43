import requests
import json
import pandas as pd
from pandas.io.json import json_normalize
from bs4 import BeautifulSoup
import re
from lxml import etree

# header
def header_1():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    }
    return headers


# request 解析json数据
def resques_json(url):
    url = url
    r = requests.get(url)
    # 解析json数据
    d = json.loads(r.text)
    return d


# requests 解析源码
def requests_soup(url,headers):
    url = url
    strhtml = requests.get(url, headers=headers)
    soup = BeautifulSoup(strhtml.text, 'lxml')
    return soup


# requests 取xpath
def requests_xpath(url):
    headers = header_1()
    r = requests.get(url,headers=headers)
    r = r.text
    htmlEmt = etree.HTML(r)
    return htmlEmt

