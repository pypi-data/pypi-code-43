from fabric import Connection

from invoke import Responder
import shutil
import os 




def install_pxf_node(conp):

    c=Connection(conp[0],connect_kwargs={"password":conp[1]})


    c.run("cp  /etc/pxf/conf/pxf-privatehdp.classpath  /etc/pxf/conf/pxf-private.classpath",pty=True)

    c.run("cp  /etc/pxf/conf/pxf-profiles.xml   /etc/pxf/conf/pxf-profiles.default.xml",pty=True,watchers=[Responder("Overwrite","y\n")])

    c.run("chown -R pxf:pxf /opt/pxf-3.3.0.0",pty=True)

    if c.run('test -d /tmp/logs',pty=True,warn=True).failed:
        c.run("mkdir /tmp/logs",pty=True)


    c.run("chown -R pxf:pxf /tmp/logs")

    if  c.run('test -h  /opt/pxf-3.3.0.0/conf',pty=True,warn=True).failed:
        c.run("ln -s /etc/pxf-3.3.0.0/conf /opt/pxf-3.3.0.0/conf",pty=True)

    if  c.run("test -h  /opt/pxf-3.3.0.0/lib" ,pty=True,warn=True).failed:
        c.run("ln -s /usr/lib/pxf  /opt/pxf-3.3.0.0/lib",pty=True)

    if  c.run("test -d /opt/pxf-3.3.0.0/conf-templates" ,pty=True,warn=True).failed:
        c.run(" mkdir /opt/pxf-3.3.0.0/conf-templates",pty=True)

    c.run("cp /opt/pxf/conf/pxf-privatehdp.classpath /opt/pxf/conf-templates/pxf-private-hdp.classpath.template",pty=True)

    if not c.run("test -f  /opt/pxf/pxf-service  " ,pty=True,warn=True).failed:
        c.run("mv /opt/pxf/pxf-service  /opt/pxf/pxf  ",pty=True)

    if not  c.run("test -h /etc/init.d/pxf-service",pty=True,warn=True).failed:
        c.run("unlink /etc/init.d/pxf-service ",pty=True)

    if c.run("test -h /etc/init.d/pxf-service",pty=True,warn=True).failed:
        c.run("ln -s /opt/pxf/pxf   /etc/init.d/pxf-service",pty=True)

    c.run("chmod 755 -R /opt/apache-tomcat/conf/",pty=True)

    if c.run("test -h /opt/pxf-3.3.0.0/apache-tomcat",pty=True,warn=True).failed:
        c.run(" ln -s /opt/apache-tomcat /opt/pxf-3.3.0.0/apache-tomcat",pty=True)

    s="""
export PARENT_SCRIPT_DIR=/opt/pxf-3.3.0.0
export PXF_HOME=/opt/pxf-3.3.0.0
export LD_LIBRARY_PATH=/usr/hdp/current/hadoop-client/lib/native:${LD_LIBRARY_PATH}
    """
    c.run("""sed -i '/\\/opt\\/pxf/d' /etc/pxf/conf/pxf-env.sh """)
    c.run("""sed -i '/hdp\\/current\\/hadoop-client/d' /etc/pxf/conf/pxf-env.sh """)
    c.run("""echo '%s' >> /etc/pxf/conf/pxf-env.sh """%s)


    c.run("""sed -i '/PARENT_SCRIPT_DIR=\\/opt\\/pxf-3.3.0.0/d'  /opt/pxf-3.3.0.0/pxf  """)
    c.run("""sed -i '/PXF_HOME=\\/opt\\/pxf-3.3.0.0/d'  /opt/pxf-3.3.0.0/pxf  """)
    c.run("""sed -i '3a\\export PARENT_SCRIPT_DIR=/opt/pxf-3.3.0.0'  /opt/pxf-3.3.0.0/pxf """)
    c.run("""sed -i '3a\\export PXF_HOME=/opt/pxf-3.3.0.0'  /opt/pxf-3.3.0.0/pxf """)

    s2="""
/usr/hdp/current/hadoop-client/lib/commons-beanutils-1.9.3.jar
/usr/hdp/current/hadoop-client/lib/commons-cli-1.2.jar
/usr/hdp/current/hadoop-client/lib/commons-codec-1.11.jar
/usr/hdp/current/hadoop-client/lib/commons-collections-3.2.2.jar
/usr/hdp/current/hadoop-client/lib/commons-compress-1.4.1.jar
/usr/hdp/current/hadoop-client/lib/commons-configuration2-2.1.1.jar
/usr/hdp/current/hadoop-client/lib/commons-io-2.5.jar
/usr/hdp/current/hadoop-client/lib/commons-lang-2.6.jar
/usr/hdp/current/hadoop-client/lib/commons-lang3-3.4.jar
/usr/hdp/current/hadoop-client/lib/commons-logging-1.1.3.jar
/usr/hdp/current/hadoop-client/lib/commons-math3-3.1.1.jar
/usr/hdp/current/hadoop-client/lib/commons-net-3.6.jar
/usr/hdp/current/hadoop-client/lib/jersey-core-1.19.jar
/usr/hdp/current/hadoop-client/lib/jersey-json-1.19.jar
/usr/hdp/current/hadoop-client/lib/jersey-server-1.19.jar
/usr/hdp/current/hadoop-client/lib/jersey-servlet-1.19.jar
/usr/hdp/current/hadoop-client/lib/jsr311-api-1.1.1.jar
/usr/hdp/current/hadoop-client/lib/woodstox-core-5.0.3.jar
/usr/hdp/current/hadoop-client/lib/stax2-api-3.1.4.jar
/usr/hdp/current/hadoop-client/lib/htrace-core4-4.1.0-incubating.jar
/usr/hdp/current/hadoop-client/lib/re2j-1.1.jar
/usr/hdp/3.0.0.0-1634/hbase/lib/atlas-hbase-plugin-impl/commons-configuration-1.10.jar
/usr/hdp/current/hadoop-hdfs-datanode/hadoop-hdfs-rbf.jar
/usr/hdp/current/hadoop-hdfs-datanode/hadoop-hdfs-nfs.jar
/usr/hdp/current/hadoop-hdfs-datanode/hadoop-hdfs-native-client.jar
/usr/hdp/current/hadoop-hdfs-datanode/hadoop-hdfs-httpfs.jar
/usr/hdp/current/hadoop-hdfs-datanode/hadoop-hdfs-client-3.1.0.3.0.0.0-1634.jar
/opt/pxf-3.3.0.0/lib/pxf-service-3.3.0.0.jar
/opt/pxf-3.3.0.0/lib/pxf-api-3.3.0.0.jar
/usr/lib/pxf/postgresql-42.2.1.jar
/usr/lib/pxf/mysql-connector-java-5.1.45-bin.jar
    """
    c.run("sed -i '27,$d' /etc/pxf-3.3.0.0/conf/pxf-public.classpath ",pty=True)

    c.run("""echo  "%s"  >> /etc/pxf-3.3.0.0/conf/pxf-public.classpath """%s2,pty=True)

    c.run(" cp /etc/pxf/conf/pxf-profiles.xml   /etc/pxf/conf/pxf-profiles-default.xml ",pty=True,watchers=[Responder("Overwrite","y\n")])

    c.run("source /etc/pxf/conf/pxf-env.sh",pty=True)

    c.run("chown -R pxf:pxf /opt/pxf",pty=True)
    c.run("chown -R pxf:pxf /etc/pxf-3.3.0.0/",pty=True)

    c.run("sudo -u pxf service pxf-service init",pty=True)
# c.run("cp /opt/pxf/pxf-service/webapps/pxf/WEB-INF/lib/*.jar  /opt/pxf/lib/",pty=True)



def start_pxf_node(conp):
    c=Connection(conp[0],connect_kwargs={"password":conp[1]})
    c.run("sudo -u pxf service pxf-service start",pty=False)

def restart_pxf_node(conp):
    c=Connection(conp[0],connect_kwargs={"password":conp[1]})
    c.run("sudo -u pxf service pxf-service restart",pty=False)

#conp=["root@172.16.0.13:22",'Since2015!']

def install(pin):
    for conp in pin:
        print(conp[0])
        install_pxf_node(conp)

def restart(pin):
    for conp in pin:
        print("restart host %s"%conp[0])
        restart_pxf_node(conp)

__note="""
pin=[
["root@172.16.0.10:22","Since2015!","master"],

["root@172.16.0.12:22","Since2015!","datanode1"],

["root@172.16.0.13:22","Since2015!","datanode2"],

["root@172.16.0.39:22","Since2015!","datanode3"],

["root@172.16.0.40:22","Since2015!","datanode4"],
]

install(pin)

restart(pin)
"""
def note():
    print(__note)


# pin=[
# ["root@172.16.0.10:22","Since2015!","master"],

# ["root@172.16.0.12:22","Since2015!","datanode1"],

# ["root@172.16.0.13:22","Since2015!","datanode2"],

# ["root@172.16.0.39:22","Since2015!","datanode3"],

# ["root@172.16.0.40:22","Since2015!","datanode4"],
# ]

# install_pxf_node(pin[1])
#restart(pin)
