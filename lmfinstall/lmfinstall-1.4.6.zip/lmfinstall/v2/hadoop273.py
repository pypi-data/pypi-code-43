from lmfinstall.v2 import common 
from fabric import Connection 

from invoke import Responder
import xml.etree.ElementTree as et
import os 
import os 
import re 
import time 



def env(pin,javafile):

    common.hostname(pin)

    common.dns(pin)

    common.ssh(pin)

    for conp in pin:
        common.java(conp,javafile)

def install_node(conp,spath,**krg):
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

    file_dir,file_name=os.path.split(spath)
  
    para={
    "spath":spath,
    "tpath":"/tmp/hadoopinstall",
    }
    print(para.keys())
    para.update(krg)

    install_node_(c,**para)

    ed=time.time()
    cost=int(ed-bg)
    print("耗时 %d 秒"%cost)

def install_node_(c,**krg):
    sdir=krg['spath']
    tdir=krg['tpath']
    file_dir,file_name=os.path.split(sdir)
    if c.run("test -f %s"%tdir,warn=True).failed:
        c.run("mkdir -p %s"%tdir)

    if  c.run("test -f %s/%s"%(tdir,file_name),pty=True,warn=True).failed:
        print("上传hadoop编译好压缩包")
        c.put(sdir,tdir)
    c.run("tar -zxvf %s/%s -C /opt"%(tdir,file_name),pty=True)


def install_nodes(pin,spath,**krg):
    for conp in pin:
        install_node(conp,spath)



def profile(pin):
    for conp in pin:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        c.run("""sed -i '/\\/opt\\/hadoop-2.7.3\\/bin/d'  /etc/profile  """)
        c.run("""echo "export PATH=\$PATH:/opt/hadoop-2.7.3/bin" >> /etc/profile && source /etc/profile""",pty=True)

        c.run("""sed -i '/export JAVA_HOME=\\/usr\\/java\\/jdk1.8.0_151/d'  /opt/hadoop-2.7.3/etc/hadoop/hadoop-env.sh  """)

        c.run("""echo "export PATH=\$PATH:/opt/hadoop-2.7.3/bin" >> /etc/profile && source /etc/profile""",pty=True)

        c.run("""echo "export JAVA_HOME=/usr/java/jdk1.8.0_151" >> /opt/hadoop-2.7.3/etc/hadoop/hadoop-env.sh"""
        ,pty=True)





####cfg

def init_config(pin,**krg):
    host_list=[ w[0][w[0].index("@")+1:w[0].index(":")] for w in pin]
    #host_list=[ w[2] for w in pin]
    master=host_list[0]
    para={
        "host_list":host_list,
        "master":master,
        "dfs_prefix":"/opt/hadoop-2.7.3"
    }
    para.update(krg)
    init_site(**para)
    for conp in pin:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        for name in ["core-site.xml",'hdfs-site.xml','mapred-site.xml','yarn-site.xml','slaves']:
            path=os.path.join(os.path.dirname(__file__),'hadoopconf',name)
            c.put(path,'/opt/hadoop-2.7.3/etc/hadoop')




def init_site(**krg):
    para={
        "dfs_prefix":"/opt/hadoop-2.7.3",
        "master":"172.16.0.10",
        "host_list":["localhost"]
    }
    para.update(krg)
    dfs_prefix=para["dfs_prefix"]
    master=para["master"]
    host_list=para["host_list"]
    cfg1={"fs.defaultFS":"hdfs://%s:8020"%master}
    core_site(**cfg1)
    cfg2={
        "dfs.replication":"",
        "dfs.namenode.name.dir":"file://%s/dfs/nn"%dfs_prefix,
        "dfs.namenode.checkpoint.dir":"file://%s/dfs/sn"%dfs_prefix,
        "dfs.datanode.data.dir":"file://%s/dfs/dn"%dfs_prefix,
        "dfs.namenode.secondary.http-address":"%s:50090"%master,
        "dfs.webhdfs.enabled":"true"
    }
    hdfs_site(**cfg2)
    cfg3={
        "yarn.resourcemanager.resource-tracker.address":"%s:8031"%master,
        "yarn.resourcemanager.scheduler.address":"%s:8030"%master,
        "yarn.resourcemanager.admin.address":"%s:8033"%master,
        "yarn.resourcemanager.webapp.address":"%s:8088"%master,
        "yarn.resourcemanager.address":"%s:8032"%master,
        "yarn.nodemanager.aux-services":"mapreduce_shuffle"
    }
    yarn_site(**cfg3)
    cfg4={
        "mapreduce.framework.name":"yarn",
    }
    mapred_site(**cfg4)
    hosts=("\n".join(host_list))
    slaves_site(hosts)


def core_site(tag='replace',**cfg1):
    path=os.path.join(os.path.dirname(__file__),'hadoopconf','core-site.xml')
    config(path,tag=tag,**cfg1)
def hdfs_site(tag='replace',**cfg1):
    path=os.path.join(os.path.dirname(__file__),'hadoopconf','hdfs-site.xml')
    config(path,tag=tag,**cfg1)
def mapred_site(tag='replace',**cfg1):
    path=os.path.join(os.path.dirname(__file__),'hadoopconf','mapred-site.xml')
    config(path,tag=tag,**cfg1)
def yarn_site(tag='replace',**cfg1):
    path=os.path.join(os.path.dirname(__file__),'hadoopconf','yarn-site.xml')
    config(path,tag=tag,**cfg1)


def slaves_site(hosts):
    path=os.path.join(os.path.dirname(__file__),'hadoopconf','slaves')
    with open(path,'w') as f :
        f.write(hosts)


def config(path,tag='update',**krg):
    print(tag)
    if tag=='update':
        cfg_update(path,**krg)
    else:
        cfg_replace(path,**krg)
def cfg_update(path,**krg):
    file=et.parse(path)
    root=file.getroot()

    para={}
    para.update(krg)
    for key in para.keys():
        has=False
        for property1 in root.getchildren():
            name,value=property1.getchildren()
            if name.text==key:
                value.text=para[key]
                has=True
        if not has:

            p = et.Element("property")
            name=et.Element("name")
            name.text=key 
            value=et.Element("value")
            value.text=para[key]
            p.append(name)
            p.append(value)
            root.append(p)

    file.write(path)

def cfg_replace(path,**mydict):

    root=et.Element("configuration")
    root.text="\n"

    for name,value in mydict.items():
        p=et.SubElement(root,"property")
        p.text="\n\t"
        pn=et.SubElement(p,"name")
        pn.text=name
        pv=et.SubElement(p,"value")
        pv.text=value

    with open(path,'w') as f:
        head="""<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>\n"""
        f.write(head)
        s=et.tostring(root,encoding='unicode')
        f.write(s)



####




def install(pin,java_file,hadoop_file,**krg):
    env(pin,java_file)
    install_nodes(pin,hadoop_file)
    init_config(pin,**krg)
    profile(pin)



__note="""
java_file="E:\\运维之王\\file\\jdk-8u151-linux-x64.rpm"
hadoop_file='E:\\运维之王\\file\\hadoop-2.7.3.tar.gz'



pin=[
["root@172.16.0.10:22","Since2015!","master"],

["root@172.16.0.12:22","Since2015!","datanode1"],

["root@172.16.0.13:22","Since2015!","datanode2"],

# ["root@172.16.0.39:22","Since2015!","datanode3"],

# ["root@172.16.0.40:22","Since2015!","datanode4"],
]

#init_config(pin)
install(pin,java_file,hadoop_file,dfs_prefix="/data")
"""
def note():
    print(__note)