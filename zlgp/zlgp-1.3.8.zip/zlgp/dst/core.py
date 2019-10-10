
from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
import time 
import traceback

def est_gg_meta(conp):
    user,password,ip,db,schema=conp
    sql="""
    CREATE TABLE dst.gg_meta (
    html_key bigint,
    guid text,
    gg_name text,
    href text,
    fabu_time timestamp,
    ggtype text,
    jytype text,
    diqu text,
    quyu text,
    info text,
    create_time timestamp,
    xzqh text,
    ts_title text,
    bd_key bigint,
    person text,
    price text,

    zhaobiaoren text ,

    zhongbiaoren  text ,

    zbdl   text ,

    zhongbiaojia float ,

    kzj  float ,

    xmmc  text ,

    xmjl text ,

    xmjl_zsbh text ,



    xmdz  text , 

    zbfs text ,

    xmbh  text ,

    mine_info text 
    )
    distributed by(html_key)
    partition by list(quyu)
      (partition hunan_huaihua_gcjs values('hunan_huaihua_gcjs'),
        partition hunan_changde_zfcg values('hunan_changde_zfcg')
        )

    """
    db_command(sql,dbtype='postgresql',conp=conp)



#为 gg表新增\删除分区
def add_partition_gg_meta(quyu,conp):
    user,password,ip,db,schema=conp
    sql="alter table dst.gg_meta add partition %s values('%s')"%(quyu,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)

def drop_partition_gg_meta(quyu,conp):
    user,password,ip,db,schema=conp
    sql="alter table dst.gg_meta drop partition for('%s')"%(quyu)
    db_command(sql,dbtype='postgresql',conp=conp)



#通用anhui_chaohu_ggzy
def update_gg_meta_prt1(quyu,conp):

    user,password,ip,db,schema=conp

    sql="""
    insert into dst.gg_meta_1_prt_anhui_chaohu_ggzy(html_key    ,guid   ,gg_name,   href    ,fabu_time, ggtype  ,jytype,    diqu    ,quyu,  info
    ,   create_time ,xzqh   ,ts_title   
    ,bd_key ,person ,price  ,zhongbiaoren   ,zhaobiaoren    ,zbdl   ,zhongbiaojia   ,kzj    ,xmmc   ,xmjl   ,xmjl_zsbh  ,xmdz   
    ,zbfs   ,xmbh   ,mine_info)
    with a as (select html_key, guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu,   quyu,   info,   create_time 
    ,dst.parse_diqu_code(quyu,page) as xzqh,dst.title2ts(gg_name) as ts_title
    from src.t_gg as t1  where quyu='anhui_chaohu_ggzy' 

    and not exists(select 1 from dst.gg_meta_1_prt_anhui_chaohu_ggzy  as t2 where t2.html_key=t1.html_key )
    )

    ,b as (select html_key, dst.kv(minfo) as info  from algo.m_gg where  quyu='anhui_chaohu_ggzy')

    ,c as (select html_key
    ,algo.get_js_v(info,'zhongbiaoren') as zhongbiaoren 
    ,algo.get_js_v(info,'zhaobiaoren') as zhaobiaoren 
    ,algo.get_js_v(info,'zbdl') as zbdl
    ,algo.get_js_v(info,'zhongbiaojia') as zhongbiaojia
    ,algo.get_js_v(info,'kzj') as kzj
    ,algo.get_js_v(info,'xmmc') as xmmc
    ,algo.get_js_v(info,'xmjl') as xmjl
    ,algo.get_js_v(info,'xmdz') as xmdz
    ,algo.get_js_v(info,'zbfs') as zbfs
    ,algo.get_js_v(info,'xmbh') as xmbh
     from b )
    ,d as (
    select a.*
    ,t3.bd_key  
    ,coalesce(zhongbiaoren,zhaobiaoren,zbdl) person 
    ,coalesce(zhongbiaojia,kzj)  price
    ,zhongbiaoren 
    ,zhaobiaoren
    ,zbdl
    ,zhongbiaojia::float     zhongbiaojia
    ,kzj::float kzj     
    ,xmmc   
    ,xmjl   
    ,null as xmjl_zsbh  
    ,xmdz   
    ,zbfs   
    ,xmbh   
    ,null::text  mine_info
     from a  left join bid.t_bd_gg  as t3 on a.html_key=t3.html_key and t3.quyu='anhui_chaohu_ggzy' left join c  on a.html_key=c.html_key )
    select * from d  
    """
    sql=sql.replace('anhui_chaohu_ggzy',quyu)
    db_command(sql,dbtype='postgresql',conp=conp)


def update_gg_meta_prt2(quyu,conp):

    user,password,ip,db,schema=conp

    sql="""
    insert into dst.gg_meta_1_prt_zlsys_yunnan_qujingshi(html_key   ,guid   ,gg_name,   href    ,fabu_time, ggtype  ,jytype,    diqu    ,quyu,  info
    ,   create_time ,xzqh   ,ts_title   
    ,bd_key ,person ,price  ,zhongbiaoren   ,zhaobiaoren    ,zbdl   ,zhongbiaojia   ,kzj    ,xmmc   ,xmjl   ,xmjl_zsbh  ,xmdz   
    ,zbfs   ,xmbh   ,mine_info)
    with a as (
    select html_key,    guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu,   quyu,   info,   create_time 
    ,dst.parse_diqu_code(quyu,page) as xzqh
    ,dst.title2ts(gg_name) as ts_title

    ,algo.get_js_v(info,'zhongbiao_hxr') as zhongbiaoren

    ,algo.get_js_v(info,'zbr') as zhaobiaoren
    ,algo.get_js_v(info,'zbdl') as zbdl  
    ,algo.get_js_v(info,'zhongbiaojia') as zhongbiaojia
    ,algo.get_js_v(info,'kzj') as kzj
    ,algo.get_js_v(info,'xm_name') as xmmc
    ,algo.get_js_v(info,'xmjl') as xmjl
    ,algo.get_js_v(info,'bd_dz') as xmdz
    ,Null::text as zbfs
    ,algo.get_js_v(info,'bd_bh') as xmbh
    from src.t_gg as t1  where quyu='zlsys_yunnan_qujingshi'
    and not exists(select 1 from dst.gg_meta_1_prt_zlsys_yunnan_qujingshi  as t2 where t2.html_key=t1.html_key 
     )
    )

    ,b as (
    select 
    a.html_key, guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu,   a.quyu, info,   create_time 
    ,xzqh,ts_title
    ,t3.bd_key  
    ,coalesce(zhongbiaoren,zhaobiaoren,zbdl) person 
    ,coalesce(zhongbiaojia,kzj)  price
    ,zhongbiaoren 
    ,zhaobiaoren
    ,zbdl
    ,zhongbiaojia::float     zhongbiaojia
    ,kzj::float kzj     
    ,xmmc   
    ,xmjl   
    ,algo.get_js_v(info,'xmjl_zsbh') as xmjl_zsbh
    ,xmdz   
    ,zbfs   
    ,xmbh   
    ,null::text  mine_info
     from a  left join bid.t_bd_gg  as t3 on a.html_key=t3.html_key and t3.quyu='zlsys_yunnan_qujingshi'  )

    select * from b  

    """
    sql=sql.replace('zlsys_yunnan_qujingshi',quyu)
    db_command(sql,dbtype='postgresql',conp=conp)


def update_gg_meta_prt3(quyu,conp):
    sql="""
        insert into dst.gg_meta_1_prt_zlshenpi_fujiansheng(html_key   ,guid   ,gg_name,   href    ,fabu_time, ggtype  ,jytype,    
        diqu    ,quyu,  info
        ,   create_time ,xzqh   ,ts_title  )

        select html_key,    guid,   gg_name,    href,   fabu_time, '拟建项目'::text as  ggtype, '拟建项目'::text as jytype, diqu,   quyu,

        dst.zlshenpi_extpage(page,fabu_time,info,quyu) as info 
                ,create_time
        ,dst.parse_diqu_code(quyu,page) as xzqh
        ,dst.title2ts(gg_name) as ts_title

        from src.t_gg as t1  where quyu='zlshenpi_fujiansheng'
        and not exists(select 1 from dst.gg_meta_1_prt_zlshenpi_fujiansheng  as t2 where t2.html_key=t1.html_key 
         )
         """
    sql=sql.replace('zlshenpi_fujiansheng',quyu)
    db_command(sql,dbtype='postgresql',conp=conp)



def update_gg_meta_prt4(quyu,conp):
    sql="""
    insert into dst.gg_meta_1_prt_zljianzhu_zljianzhu(html_key   ,guid   ,gg_name,   href    ,fabu_time, ggtype  ,jytype,    diqu    ,quyu,  info
    ,   create_time ,xzqh   ,ts_title   
    ,bd_key ,person ,price  ,zhongbiaoren   ,zhaobiaoren    ,zbdl   ,zhongbiaojia   ,kzj    ,xmmc   ,xmjl   ,xmjl_zsbh  ,xmdz   
    ,zbfs   ,xmbh   ,mine_info)
    with a as (select html_key, guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu,   quyu,   info,   create_time 
    ,dst.parse_diqu_code(quyu,page) as xzqh,dst.title2ts(gg_name) as ts_title
    from src.t_gg as t1  where quyu='zljianzhu_zljianzhu' 

    and not exists(select 1 from dst.gg_meta_1_prt_zljianzhu_zljianzhu  as t2 where t2.html_key=t1.html_key )
    )

    ,c as (select html_key
    ,algo.get_js_v(minfo,'zhongbiaoren') as zhongbiaoren 
    ,algo.get_js_v(minfo,'zhaobiaoren') as zhaobiaoren 
    ,algo.get_js_v(minfo,'zbdl') as zbdl
    ,algo.extprice(algo.get_js_v(minfo,'zhongbiaojia') )as zhongbiaojia
    ,algo.extprice(algo.get_js_v(minfo,'kzj')) as kzj
    ,algo.get_js_v(minfo,'xmmc') as xmmc
    ,algo.get_js_v(minfo,'xmjl') as xmjl
    ,algo.get_js_v(minfo,'xmdz') as xmdz
    ,algo.get_js_v(minfo,'zbfs') as zbfs
    ,algo.get_js_v(minfo,'xmbh') as xmbh
        ,algo.get_js_v(minfo,'xmjl_zsbh') as xmjl_zsbh
     from algo.m_gg where quyu='zljianzhu_zljianzhu' )
    ,d as (
    select a.*
    ,t3.bd_key  
    ,coalesce(zhongbiaoren,zhaobiaoren,zbdl) person 
    ,coalesce(zhongbiaojia,kzj)  price
    ,zhongbiaoren 
    ,zhaobiaoren
    ,zbdl
    ,zhongbiaojia::float     zhongbiaojia
    ,kzj::float kzj     
    ,xmmc   
    ,xmjl   
    ,xmjl_zsbh  
    ,xmdz   
    ,zbfs   
    ,xmbh   
    ,null::text  mine_info
     from a  left join bid.t_bd_gg  as t3 on a.html_key=t3.html_key and t3.quyu='zljianzhu_zljianzhu' left join c  on a.html_key=c.html_key )
    select * from d  
         """

    db_command(sql,dbtype='postgresql',conp=conp)

def update_gg_meta(quyu,conp):
    if quyu.startswith('zlsys'):
        update_gg_meta_prt2(quyu,conp)
    elif quyu.startswith('zlshenpi'):  
        update_gg_meta_prt3(quyu,conp)
    elif quyu.startswith('zljianzhu'):  
        update_gg_meta_prt4(quyu,conp)
    else:
        update_gg_meta_prt1(quyu,conp)

def add_quyu_tmp(quyu,conp_hawq):

    print("dst.gg_meta表更新")
    user,password,ip,db,schema=conp_hawq
    print("1、准备创建分区-%s"%quyu)
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='gg_meta' and schemaname='dst'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)

    else:
        print('%s-partition还不存在'%quyu)
        add_partition_gg_meta(quyu,conp_hawq)
    print("2、gg_meta表更新--%s"%quyu)
    update_gg_meta(quyu,conp_hawq)

def restart_quyu_tmp(quyu,conp_hawq):
    print("gg_meta表restart")
    user,password,ip,db,schema=conp_hawq
    print("1、准备restart分区-%s"%quyu)
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='gg_meta' and schemaname='dst'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)
        drop_partition_gg_meta(quyu,conp_hawq)

    else:
        print('%s-partition还不存在'%quyu)
    add_partition_gg_meta(quyu,conp_hawq)
    print("2、准备更新gg_meta表--%s"%quyu)
    update_gg_meta(quyu,conp_hawq)


#restart_quyu_tmp('zlshenpi_fujiansheng',conp_hawq=['gpadmin','since2015','192.168.4.179','base_db','public'])
#conp_hawq=['gpadmin','since2015','192.168.169.90:5433','base_db','public']