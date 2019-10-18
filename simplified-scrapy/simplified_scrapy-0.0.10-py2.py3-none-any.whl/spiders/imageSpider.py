#!/usr/bin/python
#coding=utf-8
import os,io
from simplified_scrapy.core.spider import Spider 
class ImageSpider(Spider):
  # concurrencyPer1s=2
  name = 'meishi-image-spider'
  models = ['auto_main']
  start_urls = ['http://en.people.cn/NMediaFile/2019/0925/FOREIGN201909251608000361930267899.JPG']

  def __init__(self):
    Spider.__init__(self,self.name)
    if(not os.path.exists('images/')):
      os.mkdir('images/')
    self.url_store.resetUrls(self.start_urls)

  def afterResponse(self, response, url):
    if(response.code==200 #and (response.headers.maintype=='image' 
      #or response.headers.get('Content-Type').find('image')>=0)
      ):
      name = 'images'+url[url.rindex('/'):]
      file = io.open(name, "ab")
      file.write(response.read())
      file.close()
      return None
    else:
      html = Spider.afterResponse(self, response, url)
      return Spider.removeScripts(self, html)

  def extract(self, url,html,models,modelNames):
    url = self.listImg(html)
    if(url and len(url)):
      self.saveUrl(url)
    return Spider.extract(self, url,html,models,modelNames)