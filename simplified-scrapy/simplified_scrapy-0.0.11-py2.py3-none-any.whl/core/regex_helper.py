#!/usr/bin/python
#coding=utf-8
import re,json
import sys
if sys.version_info.major == 2:
  from xml_helper import XmlDictConfig,convert2Dic
else:
  from .xml_helper import XmlDictConfig,convert2Dic
def _getSection(html,start=None,end=None):
  s = 0
  e = len(html)
  if(start): 
    if(isinstance(start,int)): s=start
    else: s=html.find(start)
  if(end): 
    if(isinstance(end,int)): e=end
    else: e=html.find(end)
  return (s,e)
def listA(html,url=None,start=None,end=None):
  if(not html): return []
  section = _getSection(html,start,end)
  s = section[0]
  e = section[1]
  if(s < 0 or e < s): return []
  html = html[s:e]
  if(not html or html.find("<a")<0): return []

  patternLst = re.compile(u'<a[\s]+[^>]*>[\s\S]*?</a>')
  patternUrl = re.compile(u'href[\s=]+[\'"](?P<url>.*?)[\'"]') 
  patternTitle1 = re.compile(u'title[\s=]+[\'"](?P<title>.*?)[\'"]')
  patternTitle2 = re.compile(u'<a[^>]*>(?P<title>.*?)</a>')

  strA = patternLst.findall(html)
  lst=[]
  for i in strA:
    url = None
    title = None
    tmp = patternUrl.search(i)
    if tmp: url = tmp.group("url")
      
    tmp = patternTitle1.search(i)
    if tmp: title = tmp.group("title")
    if(not title):
      tmp = patternTitle2.search(i)
      if tmp: 
        title = tmp.group("title")
        title = re.compile('<[\s\S]*?>').sub('',title)

    if(url):
      lst.append({'url':url,'title':title})

  return lst
def listImg(html,url=None,start=None,end=None):
  if(not html or html.find("<img")<0): return []
  section = _getSection(html,start,end)
  s = section[0]
  e = section[1]

  if(s < 0 or e < s): return None
  html = html[s:e]
  if(not html or html.find("<img")<0): return None

  patternLst = re.compile(u'<img[\s]+[^>]*>')
  patternUrl = re.compile(u'src[\s=]+[\'"](?P<url>.*?)[\'"]') 
  patternTitle = re.compile(u'alt[\s=]+[\'"](?P<title>.*?)[\'"]')
  lstStr = patternLst.findall(html)
  lst=[]
  for i in lstStr:
    url = None
    title = None
    tmp = patternUrl.search(i)
    if tmp: 
      url = tmp.group("url")
      
    tmp = patternTitle.search(i)
    if tmp:
      title = tmp.group("title")

    lst.append({'url':url,'alt':title})
  return lst

def getElementsByTag(tag,html,start=None,end=None):
  lst=[]
  s=start
  h=html
  while True:
    obj = _getElementByTag(tag,h,s,end)
    if(obj and obj[0]):
      lst.append(obj[0])
      h=h[obj[2]:]
      s=None
      end=None
    else:
      break
  return lst

def getElementByTag(tag,html,start=None,end=None):
  obj = _getElementByTag(tag,html,start,end)
  if(obj and obj[0]):
    return obj[0]
  return None

def _getElementByTag(tag,html,start=None,end=None):
  if(not tag or not html or html.find(tag)<0): return None
  section = _getSection(html,start,end)
  s = section[0]
  e = section[1]
  if(s < 0 or e < s): return None

  html = html[s:e]
  if(not html): return None

  pattern = re.compile(u'<[\s]*'+tag+'[^>]*?>[\s\S]*?</'+tag+'>') 
  m = pattern.search(html)
  if m: 
    dom = m.group(0)
    start = html.find(dom)
    end = start+len(dom)
    tagLen = len(tag)+3
    i = html.find('>',start)
    while i>=0:
      i = html.find(tag, i, end-tagLen)
      if(i>=0):
        e = html.find('</'+tag+'>', end)
        if e<0: break
        i = end
        end = e+tagLen
        continue
    html = re.compile('[\n\t]+').sub('', html[start:end])
    e2 = html.find('>')+1
    ele = convert2Dic(html[0:e2]+'</'+tag+'>')
    ele['innerHtml']=(html[e2:len(html)-tagLen]).strip()
    innerText = re.compile('<[^>]+?>').sub('',ele['innerHtml'])
    innerText = re.compile('&nbsp;').sub(' ',innerText)
    ele['innerText']=innerText.strip()
    ele['text']=ele['innerText']
    return (ele,start,end)
  return None

def getElementByID(id,html,start=None,end=None):
  obj = getElementBy('id',id,html,start,end)
  if(obj):
    return obj[0]
  return None
  
def getTag(html, end):
  start = html.rfind('<',0,end)
  if(start >= 0):
    pattern = re.compile(u'<[\s]*?(?P<tag>[\S]*?)[\s]')
    html = html[start:end]
    tmp = pattern.search(html)
    if tmp: 
      return tmp.group("tag")
  return None

def getElementsByClass(className,html,start=None,end=None):
  lst=[]
  s=start
  h=html
  while True:
    obj = getElementBy('class',className,h,s,end)
    if(obj and obj[0]):
      lst.append(obj[0])
      h=h[obj[2]:]
      s=None
      end=None
    else:
      break
  return lst

def getElementBy(attr,value,html,start=None,end=None):
  if(not attr or not value or not html or html.find(value)<0): return None
  section = _getSection(html,start,end)
  s = section[0]
  e = section[1]
  if(s < 0 or e < s): return None

  html = html[s:e]
  if(not html): return None
  index = 0
  tag = None
  while index>=0:
    index = html.find(value,index)
    if(index<0): return None
    tag = getTag(html,index)
    if not tag: 
      index+=1
      continue
    else: break
  if not tag: return None

  pattern = re.compile(u'<[\s]*'+tag+'[^>]+?'+attr+'[=\'"\s]+'+value+'[\'"][\s\S]*?>[\s\S]*?</'+tag+'>') 
  m = pattern.search(html)
  if m: 
    dom = m.group(0)
    start = html.find(dom)
    end = start+len(dom)
    tagLen = len(tag)+3
    i = html.find('>',start)
    while i>=0:
      i = html.find(tag, i, end-tagLen)
      if(i>=0):
        e = html.find('</'+tag+'>', end)
        if e<0: break
        i = end
        end = e+tagLen
        continue
    html = re.compile('[\n\t]+').sub('', html[start:end])
    e2 = html.find('>')+1
    ele = convert2Dic(html[0:e2]+'</'+tag+'>')
    ele['innerHtml']=(html[e2:len(html)-tagLen]).strip()
    innerText = re.compile('<[^>]+?>').sub('',ele['innerHtml'])
    innerText = re.compile('&nbsp;').sub(' ',innerText)
    ele['innerText']=innerText.strip()
    ele['text']=ele['innerText']
    return (ele,start,end)
  return None

def getElementByClass(className,html,start=None,end=None):
  obj = getElementBy('class',className,html,start,end)
  if(obj):
    return obj[0]
  return None

def getElementTextByID(id,html,start=None,end=None):
  obj = getElementBy('id',id,html,start,end)
  if(obj and obj[0]):
    return obj[0]["innerHtml"]
  return None

def getElementAttrByID(id,attr,html,start=None,end=None):
  obj = getElementBy('id',id,html,start,end)
  if(obj):
    dom = obj[0]
    return dom.get(attr)
  return None


print (getElementsByTag("h1",'''
<div class="content_title">
		<h1 id="chaptertitle">21.</h1>
		<h1 id="chaptertitle">22.</h1>
    </div>
'''))