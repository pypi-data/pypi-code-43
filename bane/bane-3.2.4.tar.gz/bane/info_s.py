import requests,urllib,socket,random,time,re,threading,sys,whois,json
if  sys.version_info < (3,0):
    # Python 2.x
    from scapy.all import *
else:
    from kamene.all import *
import bs4
from bs4 import BeautifulSoup
from bane.payloads import *
if os.path.isdir('/data/data/com.termux/')==False:
    import dns.resolver
def info(u,timeout=10,proxy=None):
 '''
   this function fetchs all informations about the given ip or domain using check-host.net and returns them to the use as string
   with this format:
   'requested information: result'
    
   it takes 2 arguments:
   
   u: ip or domain
   timeout: (set by default to: 10) timeout flag for the request
   usage:
   >>>import bane
   >>>domain='www.google.com'
   >>>bane.info(domain)
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 try:
  h=''
  u='https://check-host.net/ip-info?host='+u
  c=requests.get(u, headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout).text
  soup = BeautifulSoup(c,"html.parser")
  d=soup.find_all("tr")
  for a in d:
   try:
    b=str(a)
    if "IP address" not in b:
     a=b.split('<td>')[1].split('!')[0]
     a=a.split('</td>')[0].split('!')[0]
     c=b.split('<td>')[2].split('!')[0]
     c=c.split('</td>')[0].split('!')[0]
     if "strong" in c:
      for n in ['</strong>','<strong>']:
       c=c.replace(n,"")
     if "<a" in c:
      c=c.split('<a')[0].split('!')[0]
      c=c.split('</a>')[0].split('!')[0]
     if "<img" in c:
      c=c.split('<img')[1].split('!')[0]
      c=c.split('/>')[1].split('!')[0]
     n=a.strip()+': '+c.strip()
     h+=n+'\n'
   except Exception as e:
    pass
 except Exception as e:
  pass
 return h
def nortonrate(u,logs=True,returning=False,timeout=15,proxy=None):
 '''
   this function takes any giving and gives a security report from: safeweb.norton.com, if it is a: spam domain, contains a malware...
   it takes 3 arguments:
   u: the link to check
   logs: (set by default to: True) showing the process and the report, you can turn it off by setting it to:False
   returning: (set by default to: False) returning the report as a string format if it is set to: True.
   usage:
   >>>import bane
   >>>url='http://www.example.com'
   >>>bane.nortonrate(domain)
'''
 if proxy:
  proxy={'http':'http://'+proxy}
 s=""
 try:
  if logs==True:
   print('[*]Testing link with safeweb.norton.com')
  ur=urllib.quote(u, safe='')
  ul='https://safeweb.norton.com/report/show?url='+ur
  c=requests.get(ul, headers = {'User-Agent': random.choice(ua)},proxies=proxy,timeout=timeout).text 
  soup = BeautifulSoup(c, "html.parser").text
  s=soup.split("Summary")[1].split('=')[0]
  s=s.split("The Norton rating")[0].split('=')[0]
  if logs==True:
   print('[+]Report:\n',s.strip())
 except:
  pass
 if returning==True:
  return s.strip()
def myip():
 '''
   this function is for getting your ip using: ipinfo.io
   usage:
   >>>import bane
   >>>bane.myip()
   xxx.xx.xxx.xxx
'''
 try:
   return requests.get("http://ipinfo.io/ip",headers = {'User-Agent': random.choice(ua)} ,timeout=10).text.strip()
 except:
  pass
 return ''
'''
   functions below are using: api.hackertarget.com services to gather up any kind of informations about any given ip or domain
   they take 3 arguments:
   u: ip or domain
   logs: (set by default to: True) showing the process and the report, you can turn it off by setting it to:False
   returning: (set by default to: False) returning the report as a string format if it is set to: True
   general usage:
   >>>import bane
   >>>ip='50.63.33.34'
   >>>bane.dnslookup(ip)
   >>>bane.traceroute(ip)
   etc...
'''
def who_is(u):
 import whois
 u=u.replace('www.','')
 try:
  return whois.whois(u)
 except:
  pass
 return {}
def geoip(u):
 '''
   this function is for getting: geoip informations
 '''
 try:
   r=requests.get('https://geoip-db.com/jsonp/'+u).text
   return json.loads(r.split('(')[1].split(')')[0])
 except:
  pass
 return {}
def headers(u,timeout=10,logs=True,returning=False,proxy=None):
 try:
   s=requests.session()
   a=s.get(u,headers = {'User-Agent': random.choice(ua)} ,proxies=proxy,timeout=timeout).headers
 except Exception as ex:
   return None
 if logs==True:
  for x in a:
   print("{} : {}".format(x,a[x]))
 if returning==True:
  return a
def reverseiplookup(u,timeout=10,logs=True,returning=False,proxy=None):
 '''
   this function is for: reverse ip look up
 '''
 if proxy:
  proxy={'http':'http://'+proxy}
 a=[]
 try:
  name, alias, addresslist = socket.gethostbyaddr(u)
  return a.append(name)
 except Exception as e:
  try:
   r=requests.get("https://api.hackertarget.com/reverseiplookup/?q="+u,headers = {'User-Agent': random.choice(ua)} ,proxies=proxy,timeout=timeout).text
   return r.split('\n')
  except Exception as ex:
   pass
 return []
'''
   end of the information gathering functions using: api.hackertarget.com
'''
def resolve(u,server='8.8.8.8',timeout=1,lifetime=1):
 o=[]
 r = dns.resolver.Resolver()
 r.timeout = 1
 r.lifetime = 1
 r.nameservers = ['8.8.8.8']
 a = r.query(u)
 for x in a:
  o.append(str(x))
 return o
class uscanp(threading.Thread):
 def run(self):
  global portlist
  p=por[flag2]
  data=''
  for x in range(64):
   data+=random.choice(lis)
  req=IP(dst=target)/UDP(sport=random.randint(1025,65500),dport=p)/Raw(load=data)
  s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
  s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
  s.sendto(bytes(req),(target,p))
  s.settimeout(timeout)
  d=''
  while True:
   try:
    o=''
    o+=s.recv(4096)
   except:
    pass
   if len(o)==0:
    break
   else:
    d+=o
  if len(d) > 0:
   portlist.update({p:"Open"})
  else:
   portlist.update({p:"Closed"})
  s.close()
def udp_portscan(u,ports=[53],maxtime=5):
 global flag2
 global portlist
 portlist={}
 global timeout
 timeout=maxtime
 global por
 por=ports
 global target
 target=u
 for x in range(len(por)):
   flag2=x
   uscanp().start()
   time.sleep(.001)
 while(len(portlist)!=len(ports)):
  time.sleep(.1)
 return portlist
class tscanp(threading.Thread):
 def run (self):
        global portlist
        p=por[flag2]
        s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        r = s.connect_ex((target, p))
        if r == 0:
         portlist.update({p:"Open"})
        else:
         portlist.update({p:"Closed"})
        s.close()
def tcp_portscan(u,ports=[21,22,23,25,43,53,80,443,2082,3306],maxtime=5):
 global flag2
 global portlist
 portlist={}
 global timeout
 timeout=maxtime
 global por
 por=ports
 global target
 target=u
 for x in range(len(por)):
   flag2=x
   tscanp().start()
   time.sleep(.001)
 while(len(portlist)!=len(ports)):
  time.sleep(.1)
 return portlist
