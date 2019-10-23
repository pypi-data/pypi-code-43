
import jumperDb
import jumperCommon
#import jumperOutput
#import jumperApi

def setUp(req):
  jumperDb.connect()
  jumperCommon.setRequest(req)

def print_out(v):
  return jumperCommon.print_out(v)

### API SECTION ###
def getApiData():
  return jumperApi.getApiData()
### API SECTION END ###


### COMMON SECTION ###
def setOut(v):
  return jumperCommon.setOut(v)

def getOut():
  return jumperCommon.getOut()

def getConfig(p):
  return jumperCommon.getConfig(p)

def getParam(p):
  return jumperCommon.getParam(p)

def strToken(str, pos, div):
  return jumperCommon.strToken(str, pos, div)

def router():
  return jumperCommon.router()

def output():
  return jumperCommon.output()

def debug(str):
  jumperCommon.addDebugData(str)    
### COMMON SECTION END ###
 

### DB SECTION ###
def dbConnect():
  jumperDb.connect()
  
def dbRes(sql, queryParams = {}):
  jumperDb.debug(sql)
  return jumperDb.res(sql, queryParams)

def dbResJson(sql, queryParams = {}):
  jumperDb.debug(sql)
  return jumperDb.resJson(sql, queryParams)

def dbFirstRow(sql, queryParams = {}):
  jumperDb.debug(sql)
  return jumperDb.firstRow(sql, queryParams)

def dbFullRes(sql, queryParams = {}):
  jumperDb.debug(sql)
  return jumperDb.fullRes(sql, queryParams)

def dbQuery(sql, queryParams = {}):
  jumperDb.debug(sql)
  return jumperDb.query(sql, queryParams)

def dbInsert(sql, queryParams = {}):
  jumperDb.debug(sql)
  return jumperDb.insert(sql, queryParams)
  
def dbDebug(on = True):
  jumperDb.sqlDebug(on)
### DB SECTION END ###



### OUTPUT SECTION ###
def setResponse(data):
  return jumperOutput.setResponse(data)

def hasErrors():
  return jumperOutput.hasErrors()

def setError(code, text, id = 0):
  return jumperOutput.setError(code, text, id)

def output():
  jumperOutput.setDebugData(jumperCommon.getDebugData())
  return jumperOutput.output()
### OUTPUT SECTION END ###



#dbConnect()
#setParams()
#router()
#output()