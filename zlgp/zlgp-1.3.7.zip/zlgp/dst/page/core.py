
from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
import time 
import traceback

def est_t_page(conp):
    user,password,ip,db,schema=conp
    sql="""
    create table page.t_page (
    html_key bigint,
    page text ,

    quyu  text 
    )


    partition by list(quyu)
    (partition hunan_huaihua_gcjs values('hunan_huaihua_gcjs'),
    partition hunan_changde_zfcg values('hunan_changde_zfcg')
    )

    """
    db_command(sql,dbtype='postgresql',conp=conp)

#为 gg表新增\删除分区
def add_partition_t_page(quyu,conp):
    user,password,ip,db,schema=conp
    sql="alter table %s.t_page add partition %s values('%s')"%(schema,quyu,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)

def drop_partition_t_page(quyu,conp):
    user,password,ip,db,schema=conp
    sql="alter table %s.t_page drop partition for('%s')"%(schema,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)



def update_t_page(quyu,conp):

    user,password,ip,db,schema=conp

    sql="""
    insert into page.t_page_1_prt_%s 

    select html_key ,page.tran_page(page) as page,quyu  from src.t_gg_1_prt_%s as b where 

     not exists(select 1 from page.t_page_1_prt_%s as a where a.html_key=b.html_key )

    
    """%(quyu,quyu,quyu)

    db_command(sql,dbtype='postgresql',conp=conp)



def add_quyu_tmp(quyu,conp_hawq):

    print("t_page表更新")
    user,password,ip,db,schema=conp_hawq
    print("1、准备创建分区-%s"%quyu)
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_page' and schemaname='%s'
    """%(schema)
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)

    else:
        print('%s-partition还不存在'%quyu)
        add_partition_t_page(quyu,conp_hawq)
    print("2、准备更新t_page表--%s"%quyu)
    update_t_page(quyu,conp_hawq)

def restart_quyu_tmp(quyu,conp_hawq):
    print("t_page表restart")
    user,password,ip,db,schema=conp_hawq
    print("1、准备restart分区-%s"%quyu)
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_page' and schemaname='%s'
    """%(schema)
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)
        drop_partition_t_page(quyu,conp_hawq)

    else:
        print('%s-partition还不存在'%quyu)
    add_partition_t_page(quyu,conp_hawq)
    print("2、准备更新t_page表--%s"%quyu)
    update_t_page(quyu,conp_hawq)


# conp=['gpadmin','since2015','192.168.4.179','base_db','page']

# add_quyu_tmp('anhui_anqing_ggzy',conp)


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


