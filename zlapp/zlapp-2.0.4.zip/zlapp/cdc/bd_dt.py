import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_bd_dt_quyu(quyu,conp_gp):
    sql="""
    CREATE unlogged TABLE if not exists "etl"."bd_dt_%s" (

    "html_key" int8,
    "guid" text COLLATE "default",
    "bd_key" int8,
    "gg_name" text COLLATE "default",
    "ggtype" text COLLATE "default",
    "fabu_time" timestamp(6),
    "gg_info" text COLLATE "default",
    "href" text COLLATE "default",
    "xzqh" text COLLATE "default",
    "create_time" timestamp(6)
    )
    distributed by (html_key)"""%quyu
    db_command(sql,dbtype="postgresql",conp=conp_gp)

def pre_quyu_cdc(quyu,conp_gp):
    est_bd_dt_quyu(quyu,conp_gp)
    sql="truncate table etl.bd_dt_%s;"%quyu
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)
    sql1="""
    insert into etl.bd_dt_%s(html_key,    guid,   bd_key  ,gg_name,   ggtype, fabu_time   , gg_info, href ,xzqh, create_time)
    select html_key,    guid,   bd_key  ,gg_name,   ggtype, fabu_time   ,info as gg_info,href ,xzqh,   create_time
    
    from etl.gg_meta_%s  where bd_key is not null 
    """%(quyu,quyu)

    db_command(sql1,dbtype="postgresql",conp=conp_gp)

    cnt=db_query("select count(*) from etl.bd_dt_%s "%quyu,dbtype="postgresql",conp=conp_gp).iat[0,0]
    print("etl.bd_dt_%s :此次更新数据 %d 条"%(quyu,cnt))



def et_bd_dt_quyu(quyu,conp_gp,conp_app5):
    user,passwd,host,db,schema=conp_gp
    sql="""
    drop external table if exists cdc.et_bd_dt_anhui_anqing_ggzy;
    create  external table  cdc.et_bd_dt_anhui_anqing_ggzy(
    "html_key" int8,
    "guid" text ,
    "bd_key" int8,
    "gg_name" text,
    "ggtype" text ,
    "fabu_time" timestamp(6),
    "gg_info" text ,
    "href" text ,
    "xzqh" text ,
    "create_time" timestamp(6)
    )
    LOCATION ('pxf://etl.bd_dt_anhui_anqing_ggzy?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/base_db&USER=%s&PASS=%s')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,user,passwd)

    sql=sql.replace("anhui_anqing_ggzy",quyu)

    db_command(sql,dbtype="postgresql",conp=conp_app5)

def insert_into(quyu,conp_gp,conp_app5):
    et_bd_dt_quyu(quyu,conp_gp,conp_app5)


    sql="""insert into public.bd_dt(html_key,    guid,   bd_key  ,gg_name,   ggtype, fabu_time   , gg_info, href ,xzqh, create_time)
    select html_key,    guid,   bd_key  ,gg_name,   ggtype, fabu_time   ,gg_info,href ,xzqh,   create_time
    
    from cdc.et_bd_dt_%s 
    """%quyu
    db_command(sql,dbtype="postgresql",conp=conp_app5)




# quyu="anhui_anqing_ggzy"
#conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
#conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']