#!/usr/bin/python
#coding=utf-8
"""
以新浪健康为例，二级域名采集，自动抽取文章数据
"""
from simplified_scrapy.core.spider import Spider 
from simplified_scrapy.core.utils import getTimeNow,printInfo

class XiaoShuoSpider(Spider):
  # concurrencyPer1s=2
  name = 'xiaoshuo-spider'
  start_urls = ['https://www.biqudao.cc/24_24937/']
  def sortBy(self, obj):
    return obj["title"]
  def extract(self, url, html, models, modelNames):
    try:
      html = self.removeScripts(html)
      lst=[]
      data=[]
      ele = None
      if(url["url"]=='https://www.biqudao.cc/24_24937/'):
        lstA = self.listA(html,url["url"])
        for a in lstA:
          if(a["url"].find('24_24937/') > 0):
            a["url"]='https://www.biqudao.cc'+a["url"]
            lst.append(a)
        lst.sort(key=self.sortBy,reverse=False)
      else:
        ele = self.getElementByTag("h1",html)
        if(ele and ele["text"]):
          title = ele["text"]
          ele = self.getElementByID("content",html)
          if(ele):
            content = ele["innerText"]
            data.append({"Title": title, "Content": content})

      return [{"Urls": lst, "Data": data}]
    except Exception as e:
      printInfo(e)
    
  def __getitem__(self, k):
    return self[k]
  def afterResponse(self, response, url):
    html = Spider.afterResponse(self, response, url)
    return Spider.removeScripts(self, html)
