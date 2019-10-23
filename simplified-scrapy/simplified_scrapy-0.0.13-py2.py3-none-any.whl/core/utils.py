#!/usr/bin/python
#coding=utf-8
import time,io,sys,hashlib
if sys.version_info.major == 2:
  from urlparse import urlparse
else:
  from urllib.parse import urlparse
def getTime(t):
  return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(t))
def getTimeNow():
  return getTime(time.time())
def convertTime2Str(t):
  return time.strftime('%Y-%m-%d %H:%M:%S', t)
def convertStr2Time(st):
  return time.strptime(st, "%Y-%m-%d %H:%M:%S")
def printInfo(*msgs):
    print(getTime(time.time()),msgs)

# def printError(addr,err):
#   printInfo(addr, err.message)

def saveFile(name,text):
  file = io.open(name, "w",encoding="utf-8")
  try:
    file.write(u'{}\n'.format(text))
  except Exception as err:
    printInfo(err,name)
  file.close()

def appendFile(name,text):
  file = io.open(name, "a",encoding="utf-8")
  try:
    file.write(u'{}\n'.format(text))
  except Exception as err:
    printInfo(err,name)
  file.close()

def convertUrl2Int(url,count=10):
  value = urlparse(url).netloc
  value = value.split(":")[0]
  myint=0
  for c in value:
    myint += ord(c)
  return myint % count
def md5(text):
  if sys.version_info.major == 2:
    return hashlib.md5(text).hexdigest()
  else:
    return hashlib.md5(text.encode('utf-8')).hexdigest()
  
# printInfo(convertUrl2Int('https://www.cnblogs.com/blueteer/p/10136225.html'))