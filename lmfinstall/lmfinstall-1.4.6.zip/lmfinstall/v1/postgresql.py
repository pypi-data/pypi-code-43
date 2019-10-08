from fabric import Connection

from invoke import Responder
import os 

#安装 postgresql-10.6-1-linux-x64.run
#pg安装平台是 centos 7.3
#测试在win7 上运程为cent7.3 安装 postgresql-10.6-1-linux-x64.run 成功


# postgresql的安装教程
# postgresql 分为软件部分 和数据目录部分
# 常见目录
# /opt/PostgreSQL/10
# /opt/PostgreSQL/10/data
#/PGDATA/pg_hba.conf 控制访问
#/PGDATA/postgresql.conf 是数据库配置


def install(conp,spath,**krg):

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


    print("Ensure that the installed file must be postgresql-10.6-1-linux-x64.run !")

    para={
    "spath":spath,  
    "tpath":"/root/lmfinstall/postgresql-10.6",
    "pgdata":"",
    "plpython":"plpython34"
    }

    para.update(krg)
    print(para.keys())
    sdir=para["spath"]
    tdir=para["tpath"]
    pgdata=para["pgdata"]
    con=c

    #/pgdownlaod/postgresql-10.6-1-linux-x64.run 在window上相当于终端所在盘X:/pgdownlaod/postgresql-10.6-1-linux-x64.run
    if con.run("test -f %s"%tdir,warn=True).failed:
        con.run("mkdir -p %s"%tdir)
    #if con.run("test -f /root", warn=True).failed:

    con.put(sdir,tdir)

    #x2=con1.run("test -f /opt/mydata/myfile", warn=True).failed

    con.run("chmod +x %s/postgresql-10.6-1-linux-x64.run"%tdir)
    pgasw1=Responder("Installation Directory","\n")
    pgasw2=Responder("PostgreSQL Server \[Y/n\]","y\n")
    pgasw3=Responder("pgAdmin 4 \[Y/n\]","n\n")
    pgasw4=Responder("Stack Builder \[Y/n\]","y\n")
    pgasw5=Responder("Command Line Tools \[Y/n\]","y\n")
    pgasw6=Responder("Is the selection above correct","y\n")
    pgasw7=Responder("Data Directory ","%s\n"%pgdata)
    pgasw8=Responder("Password ","since2015\n")
    pgasw9=Responder("Retype password","since2015\n")
    pgasw10=Responder("Press \[Enter\] to continue","\n")

    pgasw11=Responder("Port \[5432\]","\n")
    #pgasw12=Responder("Please choose an option \[1\]","764\n")
    con.run("%s/postgresql-10.6-1-linux-x64.run"%tdir,pty=True,watchers=[pgasw1,pgasw2,pgasw3,pgasw4,
        pgasw5,pgasw6,pgasw7,pgasw8,pgasw9,pgasw10,pgasw11
        #,pgasw12
        ])
    
    if pgdata=='':
        pgdata='/opt/PostgreSQL/10/data'
    print("pgdata is : %s"%pgdata)
    cfg1(con,pgdata)
    if  para["plpython"]!='plpython34':
        version=para["plpython"]
        plpython(con,version)





def cfg1(c,pgdata):
    c.run("""echo  'host all all all md5' >>%s/pg_hba.conf"""%pgdata,pty=True)
    c.run("""systemctl restart postgresql-10""",pty=True)

def plpython(c,version):

    dir=os.path.join(os.path.dirname(__file__),'plpython','%s.so'%version)
    print(dir)
    c.put(dir,'/opt/PostgreSQL/10/lib/postgresql/')
    c.run("rm -rf /opt/PostgreSQL/10/lib/postgresql/plpython3.so")
    c.run("mv /opt/PostgreSQL/10/lib/postgresql/%s.so /opt/PostgreSQL/10/lib/postgresql/plpython3.so"%version)
    c.run("chmod -R 755  /opt/PostgreSQL/10/lib/postgresql/plpython3.so")
    c.run("chown root:daemon  /opt/PostgreSQL/10/lib/postgresql/plpython3.so")



__note="""

使用示例
conp=["root@172.16.0.10:22","Since2015!"] or ["root@172.16.0.10:22"] or "root@172.16.0.10:22"
spath="/root/postgresql-10.6-1-linux-x64.run"
**krg
install(["root@172.16.0.10:22"],"/root/postgresql-10.6-1-linux-x64.run",pgdata="/data/postgresql",plpython="plpython35")
"""
def note():
    print(__note)

# conp=["root@172.16.0.10:22","Since2015!"]
# # file="E:\\pgdownlaod\\postgresql-10.6-1-linux-x64.run"
# c=Connection(conp[0],connect_kwargs={"password":conp[1]})
# # install(conp,file)
# plpython(c,'plpython35')
