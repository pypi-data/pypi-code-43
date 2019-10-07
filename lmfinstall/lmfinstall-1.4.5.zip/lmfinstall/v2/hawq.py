from lmfinstall.v2 import common 

from fabric import Connection




def base(pin,java_file):

    common.hostname(pin)

    common.dns(pin)

    common.ssh(pin)
    #java_file="E:\\运维之王\\file\\jdk-8u151-linux-x64.rpm"
    for w in pin :
        conp=w[:2]
        common.java(conp,java_file)

def repo_ambari(pin,repo_dict):

    repo1="""
[ambari]

name=ambari

baseurl=http://172.16.0.25/ambari/2.5.0.3/centos7/

enabled=1
gpgcheck=0
    """
    repo2="""
[hdp]
name=hdp.repo 

baseurl=http://172.16.0.25/HDP/2.6.0/centos7/

enabled=1

gpgcheck=0

[hdp-utlis]
name=hdp util 

baseurl=http://172.16.0.25/HDP-UTILS-1.1.0.21-centos7/

enabled=1
gpgcheck=0

[hawq-repo]

name=hawq-repo 
baseurl=http://172.16.0.25/HAWQ/hawq_rpm_packages/

enabled=1
gpgcheck=0
    """
    repo1=repo1.replace("http://172.16.0.25/ambari/2.5.0.3/centos7/",repo_dict["ambari"])

    repo2=repo2.replace("http://172.16.0.25/HDP/2.6.0/centos7/",repo_dict["hdp"])

    repo2=repo2.replace("http://172.16.0.25/HDP-UTILS-1.1.0.21-centos7/",repo_dict["hdp_utils"])


    repo2=repo2.replace("http://172.16.0.25/HAWQ/hawq_rpm_packages/",repo_dict["hawq"])

    for w in pin:
        conp=w[:2]
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})

        c.run("""echo "%s" > /etc/yum.repos.d/ambari.repo"""%repo1,pty=True)

        c.run("""echo "%s" > /etc/yum.repos.d/hdp.repo"""%repo2,pty=True)




def install(pin,java_file,repo_dict):

    base(pin,java_file)

    repo_ambari(pin,repo_dict)


__note="""
pin=[
["root@172.16.0.10:22","Since2015!","master"],

["root@172.16.0.12:22","Since2015!","datanode1"],

["root@172.16.0.13:22","Since2015!","datanode2"],

["root@172.16.0.39:22","Since2015!","datanode3"],

["root@172.16.0.40:22","Since2015!","datanode4"],
]


repo_dict={
    "ambari":"http://172.16.0.25/ambari/2.5.1.0/centos7/",

    "hdp":"http://172.16.0.25/HDP/2.6.1/centos7/3.1.0.0-78/",

    "hdp_utils":"http://172.16.0.25/HDP-UTILS-1.1.0.21-centos7/",

    "hawq":"http://172.16.0.25/HAWQ/hawq_rpm_packages/"

}

java_file="E:\\运维之王\\file\\jdk-8u151-linux-x64.rpm"

install(pin,java_file,repo_dict)


"""

def note():

    print(__note)