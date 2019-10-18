import json
from simplified_scrapy.core.spider import Spider 
from simplified_scrapy.core.redis_urlstore import RedisUrlStore
from simplified_scrapy.core.mongo_objstore import MongoObjStore
from simplified_scrapy.core.utils import getTimeNow,printInfo
class LoginDemoSpider(Spider):
  # concurrencyPer1s=2
  name = 'login-spider'
  start_urls = [{'url':'http://47.92.87.212:8080/yiye.mgt/api/push/list',
    'requestMethod':'post',
    'postData':'{"index":1,"tbName":"biaoshu","keyword":"","count":10}'}]

  # Storing URLs with redis, if you don't like this, please comment it out 
  # url_store = RedisUrlStore(name)
  # Storing Objs with mongodb, if you don't like this, please comment it out 
  # obj_store = MongoObjStore(name)

  def afterResponse(self, response, url):
    html = Spider.afterResponse(self, response, url)
    return Spider.removeScripts(self, html)
  def extract(self, url, html, models, modelNames):
    printInfo(url,models,modelNames)
    if(html):
      json.loads(html)
    return False
  def login(self):
    login_data={
      'url':'http://47.92.87.212:8080/yiye.mgt/api/pub/login',
      'headers': { 'User-Agent' : 'yazz', "Content-Type": "application/json",
        "Referer":"http://47.92.87.212:8080/yiye.mgt/view/login.jsp"
      },
      'data': {'name':'demo', 'pwd':'123456','url':'123'}
    }
    html = Spider.login(self,login_data)
    printInfo(html)
    if(html):
      obj = json.loads(html)
      return obj.get('code')==1
    return False

# test=DemoSpider()
# test.login()
