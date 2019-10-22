# -*- coding: utf-8 -*-
import os,sys,re,getopt,time
ar=sys.argv
if len(ar) <=1:
    sys.exit("请查阅相关cli文档来输入正确的命令参数")
try:
    opts, args = getopt.getopt(sys.argv[1:], 'df:n:s:', ['help','create', 'input='])
except Exception as e:
    sys.exit("请您查阅相关cli文档来输入正确的命令参数")
# print(opts, args)
f=''  #要执行的文件 test/aa,test/bb分别表示test/aa.py和test/bb.py
d=False
n=1
s='start'  #start启动  stop停止 restart重启
name=None
for v in opts:
    # print(v[1])
    if v[0] == '-d':  #守护进程运行
        d=True
    if v[0] == '-f':  #要执行的文件
        f=v[1]
    if v[0] == '-n':  #运行数量
        n=v[1]
    if v[0] == '-s':  #运行数量
        s=v[1]
    if v[0] == '--create':  #创建应用
        from kcw.create import create
        try:
            create = create()
            create.init()
            types=args[0]
            appname=args[1]
            name=args[2]
            if types=='web':
                create.appname=appname
                create.name=name
                create.webapp()
            elif types=='cli':
                create.appname=appname
                create.name=name
                create.cliapp()
            sys.exit("执行完成")
        except Exception as e:
            sys.exit("您的创建应用目录参数错误")

n=int(n)
if 'linux' in sys.platform:
    if s=='start':
        pass
    elif s=='stop':
        os.system(r"pkill python3kcw_pl")
        sys.exit()
    elif s=='restart':
        os.system(r"pkill python3kcw_plus")
    else:
        sys.exit("-s参数超出范围")
elif sys.platform == 'win32' or sys.platform == 'win64':
    if s=='start':
        pass
    elif s=='stop':
        os.system(r"taskkill  /f  /im  python3kcw_plus.exe")
        sys.exit()
    elif s=='restart':
        os.system(r"taskkill  /f  /im  python3kcw_plus.exe")
    else:
        sys.exit("-s参数超出范围")
else:
    sys.exit("不支持此操作系统",sys.platform)

f=f.split(',')
zxlist=[]
for k in f:
    if os.path.isfile(os.getcwd()+"/"+str(k)+".py"):
        result = k.split('/')
        files=result[len(result)-1]
        path=k[:-len(files)]
        kk={'path':path,'file':files+'.py'}
        zxlist.append(kk)
    else:
        sys.exit("-f参数错误，找不到相关文件:"+os.getcwd()+"/"+str(k)+".py")


# print(zxlist)
if d:
    if 'linux' in sys.platform:
        for k in zxlist:
            i=0
            while i< n:
                time.sleep(0.1)
                os.system(r"cd "+os.getcwd()+"/"+k['path']+"&& python3kcw_plus "+k['file']+" >>./log &")
                i=i+1
    elif sys.platform == 'win32' or sys.platform == 'win64':
        for k in zxlist:
            i=0
            while i< n:
                time.sleep(0.1)
                os.system(r"cd "+os.getcwd()+"/"+k['path']+"&& start /b python3kcw_plus "+k['file'])
                i=i+1
    else:
        sys.exit("此操作系统不支持-d方式运行")
else:
    for k in zxlist:
        i=0
        while i< n:
            time.sleep(0.1)
            os.system(r"cd "+os.getcwd()+"/"+k['path']+"&& python3kcw_plus "+k['file'])
            i=i+1
