#!/usr/bin/python
#coding=utf-8
import time
from simplified_scrapy.core.spider import Spider 
from simplified_scrapy.core.redis_urlstore import RedisUrlStore
from simplified_scrapy.core.mongo_objstore import MongoObjStore
from simplified_scrapy.core.mongo_htmlstore import MongoHtmlStore
from simplified_scrapy.core.mongo_urlstore import MongoUrlStore
from simplified_scrapy.core.sqlite_urlstore import SqliteUrlStore
from simplified_scrapy.core.sqlite_htmlstore import SqliteHtmlStore
# from meishi_urlstore import MeishiUrlStore
class MeishiSpider(Spider):
  # concurrencyPer1s=2
  name = 'meishi-test-spider'
  models = ['auto_main','auto_obj']
  start_urls = []
  use_cookie = False # or # cookie_store = None 
  # start_urls = ['https://www.meishichina.com/Health/','https://www.meishij.net/jiankang/',
  # 'http://www.sohu.com/tag/19580?spm=smpc.chihe-home.side-nav.19.1567069809060ucSUkxO'
  #   'http://chihe.sohu.com/','http://www.sohu.com/tag/19581?spm=smpc.chihe-home.side-nav.15.1567069809060ucSUkxO',
  #   'http://www.sohu.com/tag/68062?spm=smpc.chihe-home.side-nav.17.1567069809060ucSUkxO',
  #   'http://www.sohu.com/tag/68060?spm=smpc.chihe-home.side-nav.16.1567069809060ucSUkxO',
  #   'http://www.sohu.com/tag/19577?spm=smpc.chihe-home.side-nav.24.1567069809060ucSUkxO',
  #   'http://www.sohu.com/tag/20846?spm=smpc.chihe-home.side-nav.29.1567069809060ucSUkxO',
  #   'http://www.sohu.com/tag/22547?spm=smpc.chihe-home.side-nav.32.1567069809060ucSUkxO',
  #   'http://www.sohu.com/tag/77843?spm=smpc.tag-page.hot-spots.6.1567070531038i5uDqXS',
  # 'https://www.douguo.com/','https://www.meishic.com/','http://edu.sina.com.cn/zl/eat/','http://www.ttmeishi.com/',
  # 'http://www.someishi.com/recipe/category/',
  # 'https://www.xinshipu.com/zuofa/788340','http://www.jiaodong.net/food/']
  # Storing URLs with redis, if you don't like this, please comment it out 
  # url_store = RedisUrlStore()
  # Storing Objs with mongodb, if you don't like this, please comment it out 
  obj_store = MongoObjStore(name)
  html_store = MongoHtmlStore(name)
  url_store = MongoUrlStore(name,{"multiQueue":True})
  # url_store.resetUrls(start_urls)
  def extract(self, url, html, models, modelNames):
    if(url.get('title') and len(url.get("title"))<3):
      url['title']=''
    # if(url.find('')>0):
    obj = Spider.extract(self,url,html,models,modelNames)
    return obj

  def afterResponse(self, response, url):
    html = Spider.afterResponse(self, response, url)
    return Spider.removeScripts(self, html)
    
  def popUrl(self):
    url = Spider.popUrl(self)
    if(url and self.urlFilter(url['url'])):
      return url
    elif(url):
      return self.popUrl()
    return None

  def urlFilter(self,url):
    if(not self.isPageUrl(url)):
      return False
    includeUrls = ['Health/','jiankang/','xinxianzixun','shipinanquan','wenhua','yangsheng','zuofa','/a/','tag/19581',
                  'tag/19580','tag/68062','tag/68060','tag/19577','tag/20846','tag/22547','tag/77843','chihe.sohu',
                  'douguo.com','meishic.com/','zl/eat/','ttmeishi.com','/food/','/zuofa/','someishi.com']

    notIncludeUrls = ['/Video','/about/']
    for n in notIncludeUrls:
      if(url.find(n)>0): return False

    for u in includeUrls:
      if(url.find(u) > 0):
        return True
    return False

  def plan(self):
    return []#[{'hour':10,'minute':10}]