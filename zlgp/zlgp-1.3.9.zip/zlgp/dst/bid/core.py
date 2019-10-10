import hashlib
from lmf.dbv2 import db_command ,db_query,db_write

import os 
import pandas as pd 

def cut(a,b):
    i=5
    tmp=a[:i]
    while tmp!=a:
        if not b.startswith(tmp):
            break
        i+=1
        tmp=a[:i]
    if len(a)!=0 and len(b)!=0:
        if not max(i/len(a),i/len(b))>0.6:return None
    if tmp==a and b.startswith(tmp):target=tmp 
    else:
        target=tmp[:-1]
    return target


def count_str(word,trr):
    k=0 
    for w in trr:
        if word in w:k+=1
    return k 
def get_bdname(word,arr,hx=None):
    if hx is not None:
        for w in hx:
            if w in word :return w
    target=word
    j=1
    ptmp=None
    trr=arr[ max(arr[arr==word].index[0]-10,0) :arr[arr==word].index[0]+10]

    data=[]
    for w in trr :

        tmp=cut(target,w)
        if  tmp is  None:continue

        k=count_str(tmp,trr)

        if k!=1 and k<=5 and tmp!=word:data.append((tmp,k))


    data.sort(key=lambda x:x[1])
    if data==[]:return None 
    target=data[0][0]
    return target

def get_bdlist(arr,cdc=None,hx=None):
    data=[]
    if cdc is not None:trr=cdc 
    else:trr=arr
    for w in trr:
        target=get_bdname(w,arr,hx)
        if target is not None:data.append(target)
    data=list(set(data))
    return data

######上面是算法



def md5hex(s):
    m=hashlib.md5(s.encode())

    x1=m.hexdigest()
    return x1 


def est_func(conp):
    #conp=['gpadmin','since2015','192.168.4.179','base_db','bid']
    sql="""
create or replace function  bid.md5hex(name_quyu text) returns text 

as $$

import hashlib 
if name_quyu is None:return None
m=hashlib.md5(name_quyu.encode())

x1=m.hexdigest()
return x1 

$$ language plpython3u;
    """
    #conp=['gpadmin','since2015','192.168.4.179','base_db','bid']

    db_command(sql,dbtype="postgresql",conp=conp)


def est_t_bd(conp):
    #conp=['gpadmin','since2015','192.168.4.179','base_db','bid']
    user,password,ip,db,schema=conp
    sql="""
    create table bid.t_bd (
    bd_key  serial,
    bd_guid text not null ,
    bd_name text not null ,
    quyu text  not null )
    distributed by (bd_key)
    partition by list(quyu)
      (partition hunan_huaihua_gcjs values('hunan_huaihua_gcjs'),
        partition hunan_changde_zfcg values('hunan_changde_zfcg')
        )

    """ 
    db_command(sql,dbtype='postgresql',conp=conp)

#为 gg表新增\删除分区
def add_partition_t_bd(quyu,conp):
    #conp=['gpadmin','since2015','192.168.4.179','base_db','bid']
    user,password,ip,db,schema=conp
    sql="alter table bid.t_bd add partition %s values('%s')"%(quyu,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)

def drop_partition_t_bd(quyu,conp):
    #conp=['gpadmin','since2015','192.168.4.179','base_db','bid']
    user,password,ip,db,schema=conp
    sql="alter table bid.t_bd drop partition for('%s')"%(quyu)
    db_command(sql,dbtype='postgresql',conp=conp)


def est_cdc_t_bd(quyu,conp,conp_pg_zlmine):
    #conp=["gpadmin",'since2015','192.168.4.179','base_db','cdc']
    sql="""drop external table if exists cdc.t_bd_cdc_hunan_huaihua_gcjs;
    create  external table cdc.t_bd_cdc_hunan_huaihua_gcjs(bd_guid text,bd_name text,quyu text ) 
    LOCATION ('pxf://t_bd.t_bd_cdc_hunan_huaihua_gcjs?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.201:5432/zlmine&USER=postgres&PASS=since2015')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """
    sql=sql.replace('hunan_huaihua_gcjs',quyu)
    sql=sql.replace("192.168.4.201",conp_pg_zlmine[2])
    db_command(sql,dbtype="postgresql",conp=conp)

####爬虫的标段
def out_t_bd_pc_all(quyu,conp,conp_pg_zlmine):
    path1=os.path.join('/data/lmf',"t_bd_cdc_%s.csv"%quyu)
    print(path1)
    #conp=['gpadmin','since2015','192.168.4.179','base_db','bid']


    sql="select gg_name from src.t_gg_1_prt_%s order by gg_name"%quyu

    df=db_query(sql,dbtype="postgresql",conp=conp)

    arr=df['gg_name']
    data=get_bdlist(arr)
    df=pd.DataFrame({"bd_name":data})
    df['quyu']=quyu 
    df['bd_guid']=df['bd_name'].map(lambda x:md5hex(x+quyu))
    df=df[['bd_guid','bd_name','quyu']]
    # print("输出df到 csv")
    # df.to_csv(path1,index=False,chunksize=5000,sep='\001',quotechar='\002')
    #conp_pg_zlmine=['postgres','since2015','192.168.4.201','zlmine','t_bd']
    db_write(df,"t_bd_cdc_%s"%quyu,dbtype="postgresql",conp=conp_pg_zlmine) 

def out_t_bd_pc_cdc(quyu,conp,conp_pg_zlmine):
    path1=os.path.join('/data/lmf',"t_bd_cdc_%s.csv"%quyu)
    print(path1)
    #conp=['gpadmin','since2015','192.168.4.179','base_db','bid']


    sql="select gg_name from src.t_gg_1_prt_%s order by gg_name"%quyu

    df=db_query(sql,dbtype="postgresql",conp=conp)

    arr=df['gg_name']
    #cdc=
    sql="select gg_name from src.t_gg_1_prt_%s order by html_key desc limit 1000"%quyu

    df=db_query(sql,dbtype="postgresql",conp=conp)

    cdc=df['gg_name']
    #hx
    sql="select bd_name from bid.t_bd_1_prt_%s "%quyu

    df=db_query(sql,dbtype="postgresql",conp=conp)

    hx=set(df['bd_name'].values)

    data=get_bdlist(arr,cdc,hx)
    df=pd.DataFrame({"bd_name":data})
    df['quyu']=quyu 
    df['bd_guid']=df['bd_name'].map(lambda x:md5hex(x+quyu))
    df=df[['bd_guid','bd_name','quyu']]

    # df.to_csv(path1,index=False,chunksize=5000,sep='\001',quotechar='\002')
    db_write(df,"t_bd_cdc_%s"%quyu,dbtype="postgresql",conp=conp_pg_zlmine) 



def update_t_bd_pc(quyu,conp):
    #conp=['gpadmin','since2015','192.168.4.179','base_db','bid']
    user,password,ip,db,schema=conp

    sql="""
    insert into bid.t_bd_1_prt_%s(bd_guid,bd_name,quyu)
    SELECT 
    distinct on(bd_guid)
    bd_guid,bd_name,quyu

     FROM cdc.t_bd_cdc_%s a where   not exists (select 1 from bid.t_bd_1_prt_%s as b where   a.bd_guid=b.bd_guid)  
    
    """%(quyu,quyu,quyu)

    db_command(sql,dbtype='postgresql',conp=conp)


def add_quyu_tmp_pc(quyu,conp_hawq,conp_pg_zlmine,tag='all'):
    #conp_hawq=['gpadmin','since2015','192.168.4.179','base_db','bid']
    print("bid.t_bd表更新")
    user,password,ip,db,schema=conp_hawq
    print("1、准备创建分区")
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_bd' and schemaname='bid'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)

    else:
        print('%s-partition还不存在'%quyu)
        add_partition_t_bd(quyu,conp_hawq)

    print("2、准备创建外部表")

    sql="""
    select tablename from pg_tables where schemaname='cdc'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    ex_tb='t_bd_cdc_%s'%quyu
    if ex_tb in df["tablename"].values:
        print("外部表%s已经存在"%quyu)

    else:
        print('外部表%s还不存在'%quyu)
        est_cdc_t_bd(quyu,conp_hawq,conp_pg_zlmine)

    print("3、准备从RDBMS导出csv")
    if tag=='all':

        out_t_bd_pc_all(quyu,conp_hawq,conp_pg_zlmine)
    else:
        out_t_bd_pc_cdc(quyu,conp_hawq,conp_pg_zlmine)


    print("4、hawq中执行更新、插入语句")

    update_t_bd_pc(quyu,conp_hawq)

def restart_quyu_tmp_pc(quyu,conp_hawq,conp_pg_zlmine):
    #conp_hawq=['gpadmin','since2015','192.168.4.179','base_db','bid']
    print("bid.t_bd 一个区域rebuild")
    user,password,ip,db,schema=conp_hawq
    print("1、准备删除分区")
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_bd' and schemaname='bid'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在,删之"%quyu)
        drop_partition_t_bd(quyu,conp_hawq)

    else:
        print('%s-partition还不存在'%quyu)

    add_quyu_tmp_pc(quyu,conp_hawq,conp_pg_zlmine,'all')


#######



def add_quyu_zlsys(quyu,conp_hawq):

    #conp_hawq=['gpadmin','since2015','192.168.4.179','base_db','bid']
    print("t_bd表更新")
    user,password,ip,db,schema=conp_hawq
    print("1、准备创建分区")
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_bd' and schemaname='bid'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)

    else:
        print('%s-partition还不存在'%quyu)
        add_partition_t_bd(quyu,conp_hawq)

    sql="""
    insert into bid.t_bd(bd_guid,bd_name,quyu)

    select bd_guid,bd_name,quyu from(
    SELECT
    distinct on(bd_guid)
     algo.get_js_v(info,'bd_guid')  as bd_guid

    ,algo.get_js_v(info,'bd_name')  as bd_name
     
    ,quyu 
      FROM src.t_gg where quyu='zlsys_yunnan_qujingshi' and  algo.get_js_v(info,'bd_name') is not null


    ) as t 

    where not exists(select 1 from bid.t_bd_1_prt_zlsys_yunnan_qujingshi as a where a.bd_guid=t.bd_guid)"""


    sql=sql.replace('zlsys_yunnan_qujingshi',quyu)

    db_command(sql,dbtype="postgresql",conp=conp_hawq)


def restart_quyu_zlsys(quyu,conp_hawq):
    #conp_hawq=['gpadmin','since2015','192.168.4.179','base_db','bid']
    print("bid.t_bd 一个区域rebuild")
    user,password,ip,db,schema=conp_hawq
    print("1、准备删除分区")
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_bd' and schemaname='bid'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在,删之"%quyu)
        drop_partition_t_bd(quyu,conp_hawq)

    else:
        print('%s-partition还不存在'%quyu)

    add_quyu_zlsys(quyu,conp_hawq)



# conp_hawq=['gpadmin','since2015','192.168.169.90:5433','base_db','bid']
# conp_pg_zlmine=['postgres','since2015','192.168.169.89','zlmine','t_bd']
# restart_quyu_tmp_pc('anhui_anqing_ggzy',conp_hawq,conp_pg_zlmine)
#est_func(conp)


#restart_quyu_zlsys('zlsys_yunnan_qujingshi',conp_hawq)