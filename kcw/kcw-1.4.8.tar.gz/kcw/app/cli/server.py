# -*- coding: utf-8 -*-
import os,sys,re,getopt,time
sys.path.append("../../")
ar=sys.argv
if len(ar) <=1:
    exit("请查阅修改cli文档来输入正确的命令参数")
try:
    opts, args = getopt.getopt(sys.argv[1:], 'df:n:s:', ['help', 'input='])
except Exception as e:
    exit("请查阅修改cli文档来输入正确的命令参数")
f=''  #要执行的文件 test/aa,test/bb分别表示start/test/aa.py和start/test/bb.py
d=False
n=1
s='start'  #start启动  stop停止 restart重启
for v in opts:
    # print(v[0])
    if v[0] == '-d':  #守护进程运行
        d=True
    if v[0] == '-f':  #要执行的文件
        f=v[1]
    if v[0] == '-n':  #运行数量
        n=v[1]
    if v[0] == '-s':  #运行数量
        s=v[1]
n=int(n)
if 'linux' in sys.platform:
    if s=='start':
        pass
    elif s=='stop':
        os.system(r"pkill python3flask_pl")
        exit()
    elif s=='restart':
        os.system(r"pkill python3flask_pl")
    else:
        exit("-s参数超出范围")
elif sys.platform == 'win32' or sys.platform == 'win64':
    if s=='start':
        pass
    elif s=='stop':
        os.system(r"taskkill  /f  /im  python3flask_plus.exe")
        exit()
    elif s=='restart':
        os.system(r"taskkill  /f  /im  python3flask_plus.exe")
    else:
        exit("-s参数超出范围")
else:
    exit("不支持此操作系统",sys.platform)

f=f.split(',')
zxlist=[]
for k in f:
    # print("start/"+str(k)+".py")
    if os.path.isfile("start/"+str(k)+".py"):
        result = k.split('/')
        kk={'path':"start/"+re.sub(result[len(result)-1],'',k),'file':result[len(result)-1]+'.py'}
        zxlist.append(kk)
    else:
        exit("-f参数错误，找不到相关文件")



        
if d:
    if 'linux' in sys.platform:
        for k in zxlist:
            i=0
            while i< n:
                time.sleep(0.1)
                os.system(r"cd "+k['path']+"&& python3flask_plus "+k['file']+" >>./log &")
                i=i+1
    elif sys.platform == 'win32' or sys.platform == 'win64':
        for k in zxlist:
            i=0
            while i< n:
                time.sleep(0.1)
                os.system(r"cd "+k['path']+"&& start /b python3flask_plus "+k['file'])
                i=i+1
    else:
        exit("此操作系统不支持-d方式运行")
else:
    for k in zxlist:
        i=0
        while i< n:
            time.sleep(0.1)
            os.system(r"cd "+k['path']+"&& python3flask_plus "+k['file'])
            i=i+1
