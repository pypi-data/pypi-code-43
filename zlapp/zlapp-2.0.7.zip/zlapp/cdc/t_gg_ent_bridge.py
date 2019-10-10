import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_t_gg_ent_bridge_quyu(quyu,conp_gp):
    sql="""
    CREATE unlogged TABLE if not exists "etl"."t_gg_ent_bridge_%s" (
    "html_key" int8 ,
    "href" text COLLATE "default",
    "ggtype" text COLLATE "default",
    "quyu" text COLLATE "default",
    "entname" text COLLATE "default",
    "entrole" text COLLATE "default",
    "price" numeric,
    "diqu" text COLLATE "default",
    "xzqh" text COLLATE "default",
    "fabu_time" timestamp(6),
    "gg_name" text COLLATE "default",
    "ent_key" int8
    )
    distributed by (html_key)"""%quyu
    db_command(sql,dbtype="postgresql",conp=conp_gp)

def pre_quyu_cdc(quyu,conp_gp):
    est_t_gg_ent_bridge_quyu(quyu,conp_gp)
    sql="truncate table etl.t_gg_ent_bridge_%s;"%quyu
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)
    sql1="""
    insert into etl.t_gg_ent_bridge_anhui_anqing_ggzy(html_key,   href    ,ggtype ,quyu,  entname ,entrole,   price   ,diqu,  xzqh,   fabu_time,  gg_name,    ent_key)
         with a as (SELECT html_key,href,ggtype,quyu
        ,zhongbiaoren as entname ,'中标人'::text entrole
        ,zhongbiaojia::float as price  ,diqu,xzqh,fabu_time,gg_name
         FROM etl.gg_meta_anhui_anqing_ggzy  where zhongbiaoren is not null 
         )
        ,b as (SELECT html_key,href,ggtype,quyu
        ,zhaobiaoren as entname ,'招标人'::text entrole
        ,kzj::float as price  ,diqu,xzqh,fabu_time,gg_name
         FROM etl.gg_meta_anhui_anqing_ggzy where zhaobiaoren is not null  
         )
        ,c as (SELECT html_key,href,ggtype,quyu
        ,zbdl as entname ,'招标代理'::text entrole
        ,kzj::float as price  ,diqu,xzqh,fabu_time,gg_name
         FROM etl.gg_meta_anhui_anqing_ggzy  where zbdl is not null   
         )
        , d as (
         select * from a union  select * from b union select * from c)
    select distinct on(html_key,entname,entrole) d.*,ent_key from d  left join public.qy_base as e  on d.entname=e.jgmc 
    """
    sql1=sql1.replace("anhui_anqing_ggzy",quyu)

    db_command(sql1,dbtype="postgresql",conp=conp_gp)

    cnt=db_query("select count(*) from etl.t_gg_ent_bridge_%s "%quyu,dbtype="postgresql",conp=conp_gp).iat[0,0]
    print("etl.t_gg_ent_bridge_%s :此次更新数据 %d 条"%(quyu,cnt))



def et_t_gg_ent_bridge_quyu(quyu,conp_gp,conp_app5):
    user,passwd,host,db,schema=conp_gp
    sql="""
    drop external table if exists cdc.et_t_gg_ent_bridge_anhui_anqing_ggzy;
    create  external table  cdc.et_t_gg_ent_bridge_anhui_anqing_ggzy(
    "html_key" int8 ,
    "href" text,
    "ggtype" text ,
    "quyu" text,
    "entname" text ,
    "entrole" text,
    "price" numeric,
    "diqu" text ,
    "xzqh" text ,
    "fabu_time" timestamp(6),
    "gg_name" text ,
    "ent_key" int8
    )
    LOCATION ('pxf://etl.t_gg_ent_bridge_anhui_anqing_ggzy?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/base_db&USER=%s&PASS=%s')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,user,passwd)

    sql=sql.replace("anhui_anqing_ggzy",quyu)

    db_command(sql,dbtype="postgresql",conp=conp_app5)


def insert_into(quyu,conp_gp,conp_app5):
    et_t_gg_ent_bridge_quyu(quyu,conp_gp,conp_app5)

    sql="""insert into public.t_gg_ent_bridge(html_key,   href    ,ggtype ,quyu,  entname ,entrole,   price   ,diqu,  xzqh,   fabu_time,  gg_name,    ent_key)
    select 
    html_key,   href    ,ggtype ,quyu,  entname ,entrole,   price   ,diqu,  xzqh,   fabu_time,  gg_name,    ent_key
            from cdc.et_t_gg_ent_bridge_%s 
    """%quyu
    db_command(sql,dbtype="postgresql",conp=conp_app5)





# quyu="anhui_anqing_ggzy"
# conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
# conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']