from fabric import Connection
from invoke import Responder
import shutil
import os 
from lmfinstall.v2 import common
# 整个设计，前提是，soft只有一份
# 2019-10-08  支持为非gpadmin 用户一步安装
#
#2019-10-08  支持  动态重启 data  和  增加新用户 
#


def pre1(pin):
    common.hostname(pin)
    common.dns(pin)
    common.ssh(pin)
def pre2(pin):
    for conp in pin:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        c.run("""cat > /etc/sysctl.conf << EOF

kernel.shmall = 4000000000

kernel.shmmax = 500000000
kernel.shmmni = 4096
vm.overcommit_memory = 1
vm.overcommit_ratio = 95
net.ipv4.ip_local_port_range = 10000 65535 
kernel.sem = 500 2048000 200 40960
kernel.sysrq = 1
kernel.core_uses_pid = 1
kernel.msgmnb = 65536
kernel.msgmax = 65536
kernel.msgmni = 2048
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.conf.all.arp_filter = 1
net.core.netdev_max_backlog = 10000
net.core.rmem_max = 2097152
net.core.wmem_max = 2097152
vm.swappiness = 10
vm.zone_reclaim_mode = 0
vm.dirty_expire_centisecs = 500
vm.dirty_writeback_centisecs = 100
vm.dirty_background_ratio = 0 # See Note 5
vm.dirty_ratio = 0
vm.dirty_background_bytes = 1610612736
vm.dirty_bytes = 4294967296
EOF""",pty=True,encoding='utf8')
        c.run("sysctl -p",pty=True)
        c.run("""cat > /etc/security/limits.conf <<EOF
* soft nofile 524288
* hard nofile 524288
* soft nproc 131072
* hard nproc 131072
EOF
        """,pty=True,encoding='utf8')


def soft(pin,gprpm_file,**krg):
    para={"tpath":"/root","superuser":"gpadmin"}
    para.update(krg)
    superuser=para["superuser"]
    conp=pin[0]
    c=Connection(conp[0],connect_kwargs={"password":conp[1]})
    sdir=gprpm_file
    tdir=para['tpath']
    file_dir,file_name=os.path.split(sdir)
    if c.run("test -f %s"%tdir,warn=True).failed:
        c.run("mkdir -p %s"%tdir)
    if  c.run("test -f %s/%s"%(tdir,file_name),pty=True,warn=True).failed:
        print("上传greenplum rpm")
        c.put(sdir,tdir)
    for conp in pin:
        c.run("scp %s/%s root@%s:%s "%(tdir,file_name,conp[2],tdir),pty=True)

    for conp in pin:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        if c.run("""egrep "^%s:" /etc/passwd"""%superuser,warn=True,pty=True).failed:

            c.run("useradd  %s "%superuser,pty=True)

        c.run("passwd %s"%superuser,pty=True,watchers=[Responder("password|密码","since2015\n")],encoding='utf8')

        c.run("yum install -y  epel-release  wget cmake3 git gcc gcc-c++ bison flex libedit-devel zlib zlib-devel perl-devel perl-ExtUtils-Embed",pty=True,encoding='utf8')

        c.run("yum install -y libcurl-devel bzip2 bzip2-devel net-tools libffi-devel openssl-devel",pty=True,encoding='utf8')
        c.run("""yum  install -y  libevent libevent-devel libxml2 libxml2-devel """,pty=True,encoding='utf8')


        c.run("mkdir -p  /data/greenplum",pty=True,encoding='utf8')
        c.run("chown -R %s: /data/greenplum"%superuser,encoding='utf8')
    for conp in pin:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        c.run("yum install -y  %s/%s"%(tdir,file_name),warn=True,encoding='utf8')
        #c.run("chown -R gpadmin:gpadmin /usr/local/greenplum-db",pty=True)
        c.run("chown -R %s:%s /usr/local/greenplum-db*"%(superuser,superuser),pty=True,encoding='utf8')



def data(pin,segs_pernode=3,init=True,superuser="gpadmin",data_prefix="/data/greenplum/data"):
    for conp in pin:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        if c.run("""egrep "^%s:" /etc/passwd"""%superuser,warn=True,pty=True).failed:

            c.run("useradd  %s "%superuser,pty=True)

        c.run("passwd %s"%superuser,pty=True,watchers=[Responder("password|密码","since2015\n")],encoding='utf8')
    all_nodes=[ conp[2] for conp in pin ]
    seg_nodes=all_nodes[1:]
    conp=pin[0]

    c=Connection(conp[0],connect_kwargs={"password":conp[1]})


    c.sudo("sed -i /MASTER_DATA_DIRECTORY/d /home/%s/.bashrc  "%superuser,user=superuser ,encoding='utf8')
    c.sudo("sed -i /greenplum_path.sh/d /home/%s/.bashrc  "%superuser,user=superuser ,encoding='utf8')
    c.sudo("""cat >> /home/%s/.bashrc << EOF
export MASTER_DATA_DIRECTORY=%s/master/seg-1
source /usr/local/greenplum-db/greenplum_path.sh
EOF"""%(superuser,data_prefix),user=superuser,encoding='utf8')

    common.ssh(pin,superuser)


    c.run("""su %s -c "echo '%s' > /home/%s/seg_nodes "  """%(superuser,"\n".join(seg_nodes),superuser) ,pty=True,encoding='utf8')
    standby=pin[-1][2]
    if data_prefix=='/data/greenplum/data':
        c.sudo("""mkdir -p /data/greenplum/data/master""",user=superuser,encoding='utf8')
        c.run("""su %s -c   " source /home/%s/.bashrc && gpssh -h %s -e 'mkdir -p /data/greenplum/data/master' " """%(superuser,superuser,standby),pty=True,encoding='utf8')

        c.run("""su %s -c   " source /home/%s/.bashrc && gpssh -f /home/%s/seg_nodes -e 'mkdir -p /data/greenplum/data/datap{1..%d}' " """%(superuser,superuser,superuser,segs_pernode),pty=True)
        c.run("""su %s -c   " source /home/%s/.bashrc && gpssh -f /home/%s/seg_nodes -e 'mkdir -p /data/greenplum/data/datam{1..%d}' " """%(superuser,superuser,superuser,segs_pernode),pty=True)
        c.run("""su %s -c   " source /home/%s/.bashrc && gpssh -f /home/%s/seg_nodes -e 'rm -rf /data/greenplum/data/data*/*' " """%(superuser,superuser,superuser),pty=True)
    else:
        c.run("""mkdir -p %s/master"""%data_prefix,encoding='utf8')
        for conp in pin:
            c=Connection(conp[0],connect_kwargs={"password":conp[1]})
            c.run("""mkdir -p %s"""%data_prefix,encoding='utf8')
            c.run("chown -R %s:%s %s "%(superuser,superuser,data_prefix),encoding='utf8')
        conp=pin[0]
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        c.run("""su %s -c   " source /home/%s/.bashrc && gpssh -h %s -e 'mkdir -p %s/master' " """%(superuser,superuser,standby,data_prefix),pty=True,encoding='utf8')

        c.run("""su %s -c   " source /home/%s/.bashrc && gpssh -f /home/%s/seg_nodes -e 'mkdir -p %s/datap{1..%d}' " """%(superuser,superuser,superuser,data_prefix,segs_pernode),pty=True)
        c.run("""su %s -c   " source /home/%s/.bashrc && gpssh -f /home/%s/seg_nodes -e 'mkdir -p %s/datam{1..%d}' " """%(superuser,superuser,superuser,data_prefix,segs_pernode),pty=True)
        c.run("""su %s -c   " source /home/%s/.bashrc && gpssh -f /home/%s/seg_nodes -e 'rm -rf %s/data*/*' " """%(superuser,superuser,superuser,data_prefix),pty=True)

    cmd="""cat > /home/%s/gpinitsystem_config << EOF
ARRAY_NAME="GREENPLUM-LMF"
SEG_PREFIX=seg
PORT_BASE=40000
MASTER_MAX_CONNECT=100
declare -a DATA_DIRECTORY=(/data/greenplum/data/datap1)
MASTER_HOSTNAME=mdw
MASTER_DIRECTORY=%s/master
MASTER_PORT=5432
TRUSTED_SHELL=ssh
ENCODING=UNICODE
MIRROR_PORT_BASE=50000
REPLICATION_PORT_BASE=41000
MIRROR_REPLICATION_PORT_BASE=51000
declare -a MIRROR_DATA_DIRECTORY=(/data/greenplum/data/datam1)
DATABASE_NAME=testdb
ENCODING=UTF-8
MACHINE_LIST_FILE=/home/%s/seg_nodes
EOF"""%(superuser,data_prefix,superuser)
    p="  ".join(["%s/datap%s"%(data_prefix,i+1) for i in range(segs_pernode)])
    m="  ".join(["%s/datam%s"%(data_prefix,i+1) for i in range(segs_pernode)])
    cmd=cmd.replace("/data/greenplum/data/datap1",p)
    cmd=cmd.replace("/data/greenplum/data/datam1",m)
    cmd=cmd.replace("MASTER_HOSTNAME=mdw","MASTER_HOSTNAME=%s"%pin[0][2])
    c.sudo(cmd,user=superuser,encoding='utf8')
    c.run("chown -R %s: /home/%s/gpinitsystem_config"%(superuser,superuser),encoding='utf8')

    if init:c.run("""su %s -c "source /home/%s/.bashrc && gpinitsystem -a -c /home/%s/gpinitsystem_config" """%(superuser,superuser,superuser),warn=True,encoding='utf8')


def swap(pin):
    for conp in pin:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        c.run("dd if=/dev/zero of=/var/swap bs=1024 count=10240k",pty=True)
        c.run("mkswap /var/swap",pty=True)
        c.run("mkswap -f /var/swap",pty=True)
        c.run("swapon /var/swap",pty=True)
        c.run("""echo "/var/swap  swap  swap defaults 0  0"  >>/etc/fstab  """,pty=True)

def plpython(pin,superuser='gpadmin'):
    conp=pin[0]
    c=Connection(conp[0],connect_kwargs={"password":conp[1]})
    for  f_name in os.listdir(os.path.join(os.path.dirname(__file__),'gpplpython')):
        file=os.path.join(os.path.dirname(__file__),'gpplpython',f_name)
        c.put(file,'/root/')
    for conp in pin:
        c.run("scp /root/plpython3u* root@%s:/usr/local/greenplum-db/share/postgresql/extension/"%(conp[2]),pty=True,encoding='utf8')
        c.run("scp /root/plpython3.so root@%s:/usr/local/greenplum-db/lib/postgresql/"%(conp[2]),pty=True,encoding='utf8')
        c.run("ssh %s chown -R %s:%s /usr/local/greenplum-db*"%(conp[2],superuser,superuser),pty=True,encoding='utf8')


def install(pin,gpfile_path,**krg):
    #pre1  pre2  swap  soft  data    
    para={"segs_pernode":3,"pre1":True,"pre2":True,"swap":False,"soft":True,

    "data":True,"init":True,"plpython3u":"35","superuser":"gpadmin","data_prefix":"/data/greenplum/data"}
    para.update(krg)
    if para["pre1"]:pre1(pin)
    if para["pre2"]:pre2(pin)

    superuser=para["superuser"]
    if para["soft"]:soft(pin,gpfile_path,superuser=superuser)
    if para["swap"]:swap(pin)
    if para["data"]:data(pin,para["segs_pernode"],para['init'],superuser=superuser,data_prefix=para["data_prefix"])
    if para["plpython3u"]=='35':
        print("增加plpython(%s)的支持"%para["plpython3u"])
        plpython(pin,superuser=superuser)

__note="""
pin=[
["root@172.16.0.10:22","Since2015!","mdw"] ,
["root@172.16.0.12:22","Since2015!","sdw1"] ,
["root@172.16.0.15:22","Since2015!","sdw2"] ,
["root@172.16.0.39:22","Since2015!","sdw3"] ,
#["root@172.16.0.40:22","Since2015!","sdw4"] 
] 

#gprpm_file="E:\\download\\greenplum-db-6.0.0-beta.6-rhel7-x86_64.rpm"
#pre(pin)
#soft(pin,gprpm_file)
#swap(pin)
#data(pin)
install(pin,gprpm_file,swap_tag=True)
"""
def note():
    print(__note)

# pin=[
# ["root@172.16.0.10:22","Since2015!","master"] ,
# ["root@172.16.0.12:22","Since2015!","datanode1"] ,
# #["root@172.16.0.15:22","Since2015!","datanode2"] ,
# ["root@172.16.0.39:22","Since2015!","datanode2"] ,
# #["root@172.16.0.40:22","Since2015!","sdw4"] 
# ] 
# gprpm_file="E:\\download\\greenplum-db-6.0.0-beta.6-rhel7-x86_64.rpm"
#install(pin,gprpm_file,segs_pernode=3,superuser="gpadmin1")

#install(pin,gprpm_file,segs_pernode=2,pre1=False,pre2=False,soft=False,init=False,data_prefix="/data/lmf")
#lpython(pin)

#data(pin,2,False,"gpadmin1")
#plpython(pin,"gpadmin1")