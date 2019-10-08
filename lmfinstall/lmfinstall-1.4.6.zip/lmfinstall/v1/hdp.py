from fabric import Connection
import os 
import re 

#默认已经安装好了hadoop必备环境

#配置repo
def repo(pin,krg):
    ambari_repo,hdp_repo,hdp_utils_repo,hawq_repo=krg
    # ambari_repo='http://172.16.0.25/ambari/2.5.0.3/centos7/'
    # hdp_repo='http://172.16.0.25/HDP/2.6.0/centos7/'
    # hdp_utils_repo='http://172.16.0.25/HDP-UTILS-1.1.0.21-centos7/'
    # hawq_repo='http://172.16.0.25/HAWQ/hawq_rpm_packages/'

    path=os.path.join(os.path.dirname(__file__),'hdprepo','ambari.repo')
    with open(path,'r',encoding='utf8') as f:
        lines=f.readlines()
    with open(path,'w',encoding='utf8') as f:
        for line in lines:
            line=re.sub("^baseurl=.*",'baseurl=%s'%(ambari_repo),line)
            f.write(line)

    path=os.path.join(os.path.dirname(__file__),'hdprepo','hdp.repo')
    with open(path,'r',encoding='utf8') as f:
        lines=f.readlines()
    with open(path,'w',encoding='utf8') as f:
        i=0
        for line in lines:
            if '[hdp]' in line:i+=1
            if '[hdp-utils]' in line:i+=1
            if '[hawq]' in line:i+=1
            if i==1:
                line=re.sub("^baseurl=.*",'baseurl=%s'%(hdp_repo),line)

            if i==2:
                line=re.sub("^baseurl=.*",'baseurl=%s'%(hdp_utils_repo),line)

            if i==3:
                line=re.sub("^baseurl=.*",'baseurl=%s'%(hawq_repo),line)


            f.write(line)

    for conp in pin:
        print(conp[0])
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        for name in ['ambari','hdp']:
            path=os.path.join(os.path.dirname(__file__),'hdprepo','%s.repo'%name)
            print(path)
            c.put(path,'/etc/yum.repos.d/')




#安装元数据库


#修改python验证



__note="""
krg=['http://172.16.0.25/ambari/2.5.0.3/centos7/','http://172.16.0.25/HDP/2.6.0/centos7/'
,'http://172.16.0.25/HDP-UTILS-1.1.0.21-centos7/','http://172.16.0.25/HAWQ/hawq_rpm_packages/']
pin=[
['root@172.16.0.10:22','Since2015!','master'],
['root@172.16.0.12:22','Since2015!','worker1'],
['root@172.16.0.13:22','Since2015!','worker2'],
['root@172.16.0.39:22','Since2015!','worker3'],
]

repo(pin,krg)
"""

def note():
    print(__notes)