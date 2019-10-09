#!/usr/bin/python
#coding=utf-8
import json,re,importlib,os
from core.request_helper import extractHtml

class Extracter:
  _models={
    'auto_all':{
      "Type": 2,
      "UrlDomains": "all_domain"
    },
    'auto_lst_obj':{
      "Type": 5,
      "MergeUrl": False
    },
    'auto_lst_url':{
      "Type": 4,
      "MergeUrl": False
    },
    'auto_main_2':{
      "Type": 2
    },
    'auto_main':{
      "Type": 2,
      "UrlDomains": "main_domain"
    },
    'auto_obj':{
      "Type": 3
    }
  }
  def __init__(self):
    try:
      #读文件
      self._iniModels('models/')

      print 'Extracter._models',self._models
    except Exception as err:
      print err

  def _iniModels(self, rootdir):
    try:
      if(not os.path.isdir(rootdir)):
        return
      list = os.listdir(rootdir)
      for i in range(0,len(list)):
        name = list[i]
        path = os.path.join(rootdir,name)
        if os.path.isfile(path):
          f = open(path,'r')
          print 'Extracter.name',name
          self._models[name[:-5]] = json.loads(f.read().decode('utf-8'))
          f.close()
    except Exception as err:
      print err
  def extract(self,url,html,ssp):
    mds = url.get("model")
    if(not mds):
      mds = ssp.models
    models = []
    if(mds):
      for modelName in mds:
        m = self._models.get(modelName)
        if(m):
          models.append(m)
        else:
          print 'no model ' + modelName

    return ssp.extract(url,html,models,mds)

# print  os.path.abspath(os.curdir)+'/simplified-scrapy/models/'
# print os.path.abspath('..')
