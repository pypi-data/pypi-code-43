#!/usr/bin/python
#coding=utf-8
"""
以新浪健康为例，二级域名采集，自动抽取文章数据
"""
from simplified_scrapy.core.spider import Spider 
from simplified_scrapy.core.utils import getTimeNow,printInfo
# from simplified_scrapy.core.redis_urlstore import RedisUrlStore
# from simplified_scrapy.core.mongo_objstore import MongoObjStore

class ExtractSpider(Spider):
  # concurrencyPer1s=2
  name = 'extract-spider'
  # start_urls = ['http://health.sina.com.cn/']
  def sortBy(self, obj):
    return obj["title"]
  def extract(self, url, html, models, modelNames):
    try:
      html = self.removeScripts(html)
      lstA = self.listA(html,url["url"])
      lst=[]
      for a in lstA:
        if(a["url"].find('health.sina.com.cn') > 0):
          lst.append(a)
      lst.sort(key=self.sortBy,reverse=True)
      ele = self.getElementByClass("second-title",html)
      data=[]
      if(ele):
        title = ele["innerText"]
        ele = self.getElementByID("artibody",html)
        if(ele):
          content = ele["innerHtml"]
          data.append({"Url": url["url"], "Title": title, "Content": content})

      return [{"Urls": lst, "Data": data}]
    except Exception as e:
      printInfo(e)
    
  def __getitem__(self, k):
    return self[k]
  def afterResponse(self, response, url):
    html = Spider.afterResponse(self, response, url)
    return Spider.removeScripts(self, html)
