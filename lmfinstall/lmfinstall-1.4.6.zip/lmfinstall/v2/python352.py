from fabric import Connection

from invoke import Responder

import time 
#安装python3.5.2 和必备yum包
# 2019-05-12 05:33:00  兰孟飞于深圳西乡网吧
def install(conp,spath,**krg):
    bg=time.time()

    if isinstance(conp,list) and len(conp)==2:
        conp=conp
    elif isinstance(conp,list) and len(conp)==1:
        conp.append(None)
    elif isinstance(conp,str):
        conp=[conp,None]
    else:
        print("非法输入")
    #conp=["root@172.16.0.12:22","Since2015!"]
    if conp[1] is None or conp[1]=='':
        c=Connection(conp[0])
    else:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})

    para={
    "spath":spath,
    "tpath":"/root/pythoninstall",
    "prefix":"/opt/python35",
    "enableshared":True
    }
    print(para.keys())
    para.update(krg)

    spath=para["spath"]
    tpath=para["tpath"]
    install_(c,**para)

    ed=time.time()
    cost=int(ed-bg)
    print("耗时 %d 秒"%cost)


def install_(c,**krg):
    
    # sdir="E:\\pfile\\033-airflow搭建\\airflow-file\\Python-3.5.2.tgz"
    # tdir="/root/airflowinstall"
    para={
    "prefix":"/opt/python35",
    "enableshared":True
    }
    print(para.keys())
    para.update(krg)

    sdir=para['spath']
    tdir=para['tpath']
    if c.run("test -f %s"%tdir,warn=True).failed:
        c.run("mkdir -p %s"%tdir)
    if  c.run("test -f %s/Python-3.5.2.tgz"%tdir,pty=True,warn=True).failed:
    #     c.run("rm -rf %s/Python-3.5.2.tgz"%tdir,pty=True)
    # else:
        print("上传pthon压缩包")
        c.put(sdir,tdir)

    c.run("yum install lrzsz  openssl-devel  zlib-devel  sqlite-devel gcc nfs-utils readline-devel -y ")
    c.run("tar -zxvf %s/Python-3.5.2.tgz -C /root"%tdir,pty=True)


    if para["enableshared"]:
        c.run("cd /root/Python-3.5.2 && ./configure --prefix=%s --enable-shared && make && make install"%para["prefix"],pty=True)
        if c.run("test -f /usr/lib64/libpython3.5m.so.1.0",warn=True).failed:
                c.run("ln -s /opt/python35/lib/libpython3.5m.so.1.0  /usr/lib64/libpython3.5m.so.1.0",pty=True)
    else:
        c.run("cd /root/Python-3.5.2 && ./configure --prefix=%s  && make && make install"%para["prefix"],pty=True)

    prefix1=para['prefix']
    prefix1=prefix1.replace('/','\\/')
    c.run("""sed -i '/%s\\/bin/d'  /etc/profile"""%prefix1,pty=True,warn=True)
    c.run("""echo  "export PATH=\$PATH:%s/bin"  >> /etc/profile  && source /etc/profile"""%para["prefix"],pty=True)

    c.run("%s/bin/python3 -m pip install readline -i https://pypi.douban.com/simple  "%para["prefix"],pty=True)
    c.run("%s/bin/python3 -m pip install --upgrade pip  -i https://pypi.douban.com/simple  "%para["prefix"],pty=True)



__note="""
使用示例
conp=['root@172.16.0.10:22','Since2015!']
spath=E:/python各版本/Python-3.5.2.tgz
**krg选项
prefix=/opt/python35
enableshared=True
from lmfinstall....python352 import install 
install(['root@172.16.0.10:22','Since2015!'],"E:/python各版本/Python-3.5.2.tgz")
"""

def note():
    print(__note)

#install(['root@172.16.0.10:22','Since2015!'],"E:/python各版本/Python-3.5.2.tgz")