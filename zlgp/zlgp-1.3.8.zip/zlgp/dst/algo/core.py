
from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
import time 
import traceback

def pre_func(conp):
    sql="""
create or replace function algo.extall(page text ) returns text 

as $$
 
import json 


from zlgg.extdata import extall 
from zlgg.core.words import initwords_local



if 'krr' not in GD.keys():
    
    krr,krrdict=initwords_local()

    GD['krr']=krr

krr=GD['krr']

data=extall(page,krr)
data=json.dumps(data,ensure_ascii=False)


return data 






$$ language plpython3u ;
"""
    db_command(sql,dbtype='postgresql',conp=conp)

def est_m_gg(conp):
    user,password,ip,db,schema=conp
    sql="""
    create table algo.m_gg (
    html_key bigint,
    href text  not null  ,
    ggtype text not null ,
    quyu text not null,
    minfo text
    )
    distributed by (html_key)
    partition by list(quyu)
    (partition hunan_huaihua_gcjs values('hunan_huaihua_gcjs'),
    partition hunan_changde_zfcg values('hunan_changde_zfcg')
    )

    """ 
    db_command(sql,dbtype='postgresql',conp=conp)

#为 gg表新增\删除分区
def add_partition_m_gg(quyu,conp):
    user,password,ip,db,schema=conp
    sql="alter table algo.m_gg add partition %s values('%s')"%(quyu,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)

def drop_partition_m_gg(quyu,conp):
    user,password,ip,db,schema=conp
    sql="alter table algo.m_gg drop partition for('%s')"%(quyu)
    db_command(sql,dbtype='postgresql',conp=conp)



def update_m_gg(quyu,conp):

    user,password,ip,db,schema=conp
    if quyu.startswith('zljianzhu'):
        sql="""
        insert into algo.m_gg_1_prt_%s 

        select html_key ,href,ggtype,quyu,algo.extall_zljianzhu(page) as minfo from src.t_gg as b where quyu='%s'

        and not exists(select 1 from algo.m_gg_1_prt_%s as a where a.html_key=b.html_key )

        
        """%(quyu,quyu,quyu)
    else:
        sql="""
        insert into algo.m_gg_1_prt_%s 

        select html_key ,href,ggtype,quyu,algo.extall(page) as minfo from src.t_gg as b where quyu='%s'

        and not exists(select 1 from algo.m_gg_1_prt_%s as a where a.html_key=b.html_key )

        
        """%(quyu,quyu,quyu)

    db_command(sql,dbtype='postgresql',conp=conp)



def add_quyu_tmp(quyu,conp_hawq):

    print("algo.m_gg表更新")
    user,password,ip,db,schema=conp_hawq
    print("1、准备创建分区-%s"%quyu)
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='m_gg' and schemaname='algo'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)

    else:
        print('%s-partition还不存在'%quyu)
        add_partition_m_gg(quyu,conp_hawq)
    print("2、准备更新m_gg表--%s"%quyu)
    update_m_gg(quyu,conp_hawq)

def restart_quyu_tmp(quyu,conp_hawq):
    print("algo.m_gg表restart")
    user,password,ip,db,schema=conp_hawq
    print("1、准备restart分区-%s"%quyu)
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='m_gg' and schemaname='algo'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)
        drop_partition_m_gg(quyu,conp_hawq)

    else:
        print('%s-partition还不存在'%quyu)
    add_partition_m_gg(quyu,conp_hawq)
    print("2、准备更新m_gg表--%s"%quyu)
    update_m_gg(quyu,conp_hawq)





# def add_quyus_sheng(sheng):
#     quyus=zhulong_diqu_dict[sheng]
#     bg=time.time()
#     conp=["gpadmin","since2015","192.168.4.179","base_db","m1"]
#     for quyu in quyus:
#         try:
#             add_quyu(quyu,conp)

#             ed=time.time()
#             cost=int(ed-bg)
#             print("耗时--%d秒"%cost)
#         except:
#             traceback.print_exc()
#         finally:
#             bg=time.time()

# def add_quyus_all():
#     for sheng in zhulong_diqu_dict.keys():
#         add_quyus_sheng(sheng)

#add_quyus_all()

#conp=["gpadmin","since2015","192.168.169.90:5433","base_db","algo"]


#est_m_gg(conp)