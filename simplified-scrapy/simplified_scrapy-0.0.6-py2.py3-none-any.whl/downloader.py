#!/usr/bin/python
#coding=utf-8
import json,re,importlib
import sys
if sys.version_info.major == 2:
  from core.request_helper import requestPost,requestGet
else:
  from .core.request_helper import requestPost,requestGet
  

# from yiye_common.module_helper import import_module
def execDownload(url,ssp):
  headers = url.get('cookie')
  head=None
  if(headers):
    head=json.loads(headers)
  if(url.get('requestMethod')):
    if(url.get('requestMethod').lower()=='post'):
      return requestPost(url['url'],url.get('postData'),head,url.get('useIp')==1,ssp)
    elif(url.get('requestMethod').lower()=='render'):
      return ssp.renderUrl(url)
  return requestGet(url['url'],head,url.get('useIp')==1,ssp)
