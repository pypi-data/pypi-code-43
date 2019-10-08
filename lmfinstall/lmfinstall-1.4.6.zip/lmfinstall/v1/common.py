from fabric import Connection

from invoke import Responder
import shutil
import os 



# 测试环境 centos7.3 
# 2019-05-14 中午，于兰孟飞犯困之时

# pin=[
# ["root@172.16.0.10:22","Since2015!","master"],
# ["root@172.16.0.12:22","Since2015!","worker1"],
# ["root@172.16.0.13:22","Since2015!","worker2"]
# ]
# ssh(pin)


#给计算机命名
def hostname(pin):
    """命名
    """
    for w in pin:
        conp=w[:2]
        name=w[2]
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        c.run("hostnamectl --static set-hostname %s"%name,pty=True)


#配置/etc/hosts
def dns(pin):
    tmp=[]
    for w in pin:
        ip=w[0][w[0].index("@")+1:w[0].index(":")]
        name=w[2]
        tmp_str="%s  %s"%(ip,name)
        tmp.append(tmp_str)
    myhosts="\n".join(tmp)
    for w in pin:
        conp=w[:2]
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        c.run("sed -i '3,$d' /etc/hosts",pty=True)
        c.run("""echo "%s" >> /etc/hosts"""%myhosts,pty=True)


#配置免密，基于 ssh1  tmpdir=/tmp/tmp1
def ssh(pin):
    for conp in pin:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        c.run("""ssh-keygen -t rsa  -m PEM  -b 4096 -P '' -f /root/.ssh/id_rsa  """,pty=True,watchers=[Responder("Overwrite","y\n")])
        tmpdir='/tmp/tmp1'
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        c.get("/root/.ssh/id_rsa.pub","%s/id_rsa.pub.%s"%(tmpdir,conp[2]))

    farr=os.listdir(tmpdir)
    with open(tmpdir+'/authorized_keys','w') as f :
        for w in farr:
            file=tmpdir+"/"+w
            if w.startswith('id_rsa'):
                with open(file,'r') as f1:
                    content=f1.read()
                f.write(content+"\n")

    for conp in pin:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        #c.run("""ssh-keygen -t rsa  -P '' -f /root/.ssh/id_rsa  """,pty=True,watchers=[Responder("Overwrite","y\n")])

        c.put(tmpdir+'/authorized_keys',"/root/.ssh/")
        c.run("chmod -R 700 /root/.ssh/authorized_keys")

    shutil.rmtree(tmpdir)

__note="""
配置过程:
hostname 主要利用 hostnamectl --static set-hostname xx 命令
dns 则编辑 /etc/hosts 文件 
ssh免密，注意ssh1  和 ssh2的区别
确保ssh1的方法 ssh-keygen -t rsa  -m PEM  -b 4096 -P '' -f /root/.ssh/id_rsa
搜集台机器的id_rsa.pub，全部写于authorized_kes 文件，最后放在每台机器的 /root/.ssh下
调用方法示例:
pin=[
["root@172.16.0.10:22","Since2015!","master"],
["root@172.16.0.12:22","Since2015!","worker1"],
["root@172.16.0.13:22","Since2015!","worker2"]
]
ssh(pin)
conp=["root@172.16.0.12:22","Since2015!"]
spath="E:\\pfile\\030-centos7-hdp\\hdp\\jdk-8u151-linux-x64.rpm"
java(conp,spath)
"""


def java(conp,spath,**krg):
    if isinstance(conp,list) and len(conp)==2:
        conp=conp
    elif isinstance(conp,list) and len(conp)==1:
        conp.append(None)
    elif isinstance(conp,str):
        conp=[conp]
    else:
        print("非法输入")
    #conp=["root@172.16.0.12:22","Since2015!"]
    if conp[1] is None or conp[1]=='':
        c=Connection(conp[0])
    else:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})

    para={
    "tpath":"/root"
    }

    para.update(krg)
    tpath=para['tpath']
    c.put(spath,tpath)
    c.run("yum remove jdk -y",pty=True,warn=True)
    c.run("yum install -y /root/jdk-8u151-linux-x64.rpm",pty=True)
    c.run("""echo "export JAVA_HOME=/usr/java/jdk1.8.0_151\nexport PATH=\$JAVA_HOME/bin:\$PATH\nexport CLASSPATH=.:\$JAVA_HOME/lib/dt.jar:\$JAVA_HOME/lib/tools.jar" >> /etc/profile"""
        ,pty=True)
    c.run("source  /etc/profile")


def note():
    print(__note)

