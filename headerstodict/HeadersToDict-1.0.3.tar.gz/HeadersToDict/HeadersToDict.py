def fromFile(file):
    with open(file)as f:
        headers=f.readlines()
    return dict([line.strip().split(":",1) for line in headers])

def fromStr(_str):
    return  dict([line.strip().replace(': ',':').split(':',1) for line in _str.strip().split('\n')])
def getMobile():
    headers="""
Connection: keep-alive
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Mobile Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Upgrade-Insecure-Requests: 1
    """
    return fromStr(headers)
def getChrome():
    headers="""Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: no-cache
Pragma: no-cache
Proxy-Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36
    """
    return fromStr(headers)
# a=fromFile("example")
a=getMobile()
print(a)
