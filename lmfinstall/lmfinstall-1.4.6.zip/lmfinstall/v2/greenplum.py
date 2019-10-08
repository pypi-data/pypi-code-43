from fabric import Connection

from invoke import Responder
import shutil
import os 
from lmfinstall.v2 import common




def pre(pin):
    common.hostname(pin)
    common.dns(pin)
    common.ssh(pin)
    for conp in pin:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        c.run("""cat > /etc/sysctl.conf << EOF
# sysctl settings are defined through files in
# /usr/lib/sysctl.d/, /run/sysctl.d/, and /etc/sysctl.d/.
#
# Vendors settings live in /usr/lib/sysctl.d/.
# To override a whole file, create a new file with the same in
# /etc/sysctl.d/ and put new settings there. To override
# only specific settings, add a file with a lexically later
# name in /etc/sysctl.d/ and put new settings there.
#
# For more information, see sysctl.conf(5) and sysctl.d(5).

kernel.shmmax = 500000000
kernel.shmmni = 4096
kernel.shmall = 4000000000
kernel.sem = 500 1024000 200 4096
kernel.sysrq = 1
kernel.core_uses_pid = 1
kernel.msgmnb = 65536
kernel.msgmax = 65536
kernel.msgmni = 2048
net.ipv4.tcp_syncookies = 1
net.ipv4.ip_forward = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.tcp_tw_recycle = 1
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.conf.all.arp_filter = 1
net.ipv4.ip_local_port_range = 1025 65535
net.core.netdev_max_backlog = 10000
net.core.rmem_max = 2097152
net.core.wmem_max = 2097152
vm.overcommit_memory = 2
vm.swappiness = 1
kernel.pid_max = 655350
EOF""",pty=True)
        c.run("sysctl -p",pty=True)
        c.run("""cat > /etc/security/limits.conf <<EOF
* soft nofile 65536
* hard nofile 65536
* soft nproc 131072
* hard nproc 131072
        """,pty=True)

def soft_prt1_node(conp):
    c=Connection(conp[0],connect_kwargs={"password":conp[1]})
    if c.run("""egrep "^gpadmin" /etc/passwd""",warn=True,pty=True).failed:

        c.run("useradd  gpadmin ",pty=True)

    c.run("passwd gpadmin",pty=True,watchers=[Responder("password","gpadmin\n")])

    c.run("yum install -y  epel-release  wget cmake3 git gcc gcc-c++ bison flex libedit-devel zlib zlib-devel perl-devel perl-ExtUtils-Embed",pty=True)

    c.run("yum install -y libcurl-devel bzip2 bzip2-devel net-tools libffi-devel openssl-devel",pty=True)
    c.run("""yum  install -y  libevent libevent-devel libxml2 libxml2-devel """,pty=True)


    c.run("mkdir -p  /data/greenplum",pty=True)
    c.run("chown -R gpadmin:gpadmin /data/greenplum")


def soft_prt1(pin):
    """软件部分- """
    for conp in pin:
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(conp[0])
        soft_prt1_node(conp)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


def soft_prt2(pin,gpfile_path):
    """主要利用 gpssh-exkeys gpadmin免密 和 分发软件"""
    file_name=os.path.split(gpfile_path)[1]
    conp=pin[0]
    c=Connection(conp[0],connect_kwargs={"password":conp[1]})
    c.put(gpfile_path,"/root")

    c.run("unzip /root/%s"%file_name)
    file_name1=file_name.replace('.zip','.bin')
    c.run("""/root/%s << EOF
yes
/data/greenplum/soft/greenplum-db
yes
yes
EOF  """%file_name1,pty=True)
    all_nodes=[ conp[2] for conp in pin ]
    

    c=Connection(conp[0],connect_kwargs={"password":conp[1]})

    c.sudo("sed -i /MASTER_DATA_DIRECTORY/d /home/gpadmin/.bashrc  ",user="gpadmin" )
    c.sudo("sed -i /greenplum_path.sh/d /home/gpadmin/.bashrc  ",user="gpadmin" )
    c.sudo("""cat >> /home/gpadmin/.bashrc << EOF
export MASTER_DATA_DIRECTORY=/data/greenplum/data/master/seg-1
source /data/greenplum/soft/greenplum-db/greenplum_path.sh
EOF""",user='gpadmin')

    cmd="""su gpadmin -c " source /home/gpadmin/.bashrc && gpssh-exkeys -h mdw " """ 
    cmd=cmd.replace("-h mdw"," ".join(["-h %s"%name for name in all_nodes]))
    c.run(cmd,pty="True")

    c.run("""su gpadmin -c "echo '%s' > /home/gpadmin/all_nodes "  """%("\n".join(all_nodes)) ,pty=True)

    c.run("chown -R gpadmin:gpadmin /data/greenplum")
    c.run("""su gpadmin -c   " source /home/gpadmin/.bashrc && gpseginstall -f /home/gpadmin/all_nodes -u gpadmin -p gpadmin"   """,pty=True)


def soft(pin,gpfile_path):
    soft_prt1(pin)
    soft_prt2(pin,gpfile_path)


def data(pin,segs_pernode=4):

    all_nodes=[ conp[2] for conp in pin ]
    seg_nodes=all_nodes[1:]
    conp=pin[0]
    c=Connection(conp[0],connect_kwargs={"password":conp[1]})
    c.run("""su gpadmin -c "echo '%s' > /home/gpadmin/seg_nodes "  """%("\n".join(seg_nodes)) ,pty=True)
    standby=pin[-1][2]
    c.sudo("""mkdir -p /data/greenplum/data/master""",user="gpadmin")
    c.run("""su gpadmin -c   " source /home/gpadmin/.bashrc && gpssh -h %s -e 'mkdir -p /data/greenplum/data/master' " """%standby,pty=True)

    c.run("""su gpadmin -c   " source /home/gpadmin/.bashrc && gpssh -f /home/gpadmin/seg_nodes -e 'mkdir -p /data/greenplum/data/datap{1..%d}' " """%segs_pernode,pty=True)
    c.run("""su gpadmin -c   " source /home/gpadmin/.bashrc && gpssh -f /home/gpadmin/seg_nodes -e 'mkdir -p /data/greenplum/data/datam{1..%d}' " """%segs_pernode,pty=True)

    cmd="""cat > /home/gpadmin/gpinitsystem_config << EOF
ARRAY_NAME="GREENPLUM-LMF"
SEG_PREFIX=seg
PORT_BASE=40000
MASTER_MAX_CONNECT=1000
declare -a DATA_DIRECTORY=(/data/greenplum/data/datap1)
MASTER_HOSTNAME=mdw
MASTER_DIRECTORY=/data/greenplum/data/master
MASTER_PORT=5432
TRUSTED_SHELL=ssh
ENCODING=UNICODE
MIRROR_PORT_BASE=50000
REPLICATION_PORT_BASE=41000
MIRROR_REPLICATION_PORT_BASE=51000
declare -a MIRROR_DATA_DIRECTORY=(/data/greenplum/data/datam1)
DATABASE_NAME=gpadmin
ENCODING=UTF-8
MACHINE_LIST_FILE=/home/gpadmin/seg_nodes
EOF"""
    p="  ".join(["/data/greenplum/data/datap%s"%(i+1) for i in range(segs_pernode)])
    m="  ".join(["/data/greenplum/data/datam%s"%(i+1) for i in range(segs_pernode)])
    cmd=cmd.replace("/data/greenplum/data/datap1",p)
    cmd=cmd.replace("/data/greenplum/data/datam1",m)
    c.sudo(cmd,user='gpadmin')

    c.run("""su gpadmin -c   "source /home/gpadmin/.bashrc && gpinitsystem -a -c /home/gpadmin/gpinitsystem_config" """,warn=True)





def swap(pin):
    for conp in pin:
        c=Connection(conp[0],connect_kwargs={"password":conp[1]})
        c.run("dd if=/dev/zero of=/var/swap bs=1024 count=10240k",pty=True)
        c.run("mkswap /var/swap",pty=True)
        c.run("mkswap -f /var/swap",pty=True)
        c.run("swapon /var/swap",pty=True)
        c.run("""echo "/var/swap  swap  swap defaults 0  0"  >>/etc/fstab  """,pty=True)


def install(pin,gpfile_path,**krg):
    para={"segs_pernode":4,"swap_tag":False}
    para.update(krg)
    pre(pin)
    soft(pin,gpfile_path)
    if  para["swap_tag"]:swap(pin)
    data(pin,para["segs_pernode"])

__note="""
pin=[
["root@172.16.0.10:22","Since2015!","mdw"] ,
["root@172.16.0.12:22","Since2015!","sdw1"] ,
["root@172.16.0.15:22","Since2015!","sdw2"] ,
["root@172.16.0.39:22","Since2015!","sdw3"] ,
["root@172.16.0.40:22","Since2015!","sdw4"] 
] 

gpfile_path="E:\\download\\greenplum-db-5.10.2-rhel7-x86_64.zip"

#pre(pin)
# soft(pin,gpfile_path)
#swap(pin)
#data(pin,3)
install(pin,gpfile_path,segs_pernode=3,swap_tag=True)
"""
def note():
    print(__note)

# pin=[
# ["root@172.16.0.10:22","Since2015!","mdw"] ,
# ["root@172.16.0.12:22","Since2015!","sdw1"] ,
# ["root@172.16.0.15:22","Since2015!","sdw2"] ,
# ["root@172.16.0.39:22","Since2015!","sdw3"] ,
# ["root@172.16.0.40:22","Since2015!","sdw4"] 
# ] 
# gpfile_path="E:\\download\\greenplum-db-5.12.0-rhel7-x86_64.zip"
# install(pin,gpfile_path,segs_pernode=3,swap_tag=True)