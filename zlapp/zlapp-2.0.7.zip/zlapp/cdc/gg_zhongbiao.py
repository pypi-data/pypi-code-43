import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

import time 

def est_gg_zhongbiao_quyu(quyu,conp_gp):
    sql="""
    CREATE  unlogged TABLE if not exists "etl"."gg_zhongbiao_%s" (
    "html_key" int8,
    "href" text COLLATE "default",
    "ggtype" text COLLATE "default",
    "quyu" text COLLATE "default",
    "zhongbiaoren" text COLLATE "default",
    "zhaobiaoren" text COLLATE "default",
    "zbdl" text COLLATE "default",
    "zhongbiaojia" numeric,
    "kzj" numeric,
    "xmmc" text COLLATE "default",
    "xmjl" text COLLATE "default",
    "xmjl_zsbh" text COLLATE "default",
    "xmdz" text COLLATE "default",
    "zbfs" text COLLATE "default",
    "xmbh" text COLLATE "default",
    "gg_name" text COLLATE "default",
    "fabu_time" timestamp(6),
    "xzqh" text COLLATE "default",
    "ts_title" text,
    "ent_key" int8,
    "person_key" int8
    )
    distributed by (html_key)"""%quyu
    db_command(sql,dbtype="postgresql",conp=conp_gp)






def get_max_html_key(quyu,conp_gp):
    max_html_key=db_query("select max_gg_zhongbiao from etlmeta.t_html_key where quyu='%s'"%quyu,dbtype="postgresql",conp=conp_gp).iat[0,0]

    return max_html_key

def pre_quyu_cdc(quyu,conp_gp):
    max_html_key=get_max_html_key(quyu,conp_gp)
    print("更新前最大html_key :",max_html_key)
    est_gg_zhongbiao_quyu(quyu,conp_gp)
    sql="truncate table etl.gg_zhongbiao_%s;"%quyu
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)

    sql1="""
    insert into etl.gg_zhongbiao_%s( html_key,  href ,   ggtype , quyu ,   zhongbiaoren,    zhaobiaoren ,zbdl  ,  zhongbiaojia  ,  kzj, xmmc,    xmjl ,xmjl_zsbh,   xmdz ,
           zbfs  ,  xmbh ,   gg_name, fabu_time ,  xzqh ,   ts_title,ent_key,person_key)

     with a as ( 
    select html_key,  href ,   ggtype ,quyu ,   zhongbiaoren, zhaobiaoren ,zbdl  ,zhongbiaojia::numeric zhongbiaojia  
    ,  kzj, xmmc,  xmjl ,xmjl_zsbh,   xmdz ,zbfs  ,  xmbh , gg_name,fabu_time ,  xzqh , ts_title 
        from dst.gg_meta  as  t1 
    where   zhongbiaoren is not null and html_key>%d and zhongbiaoren is not null and quyu='%s' )


    select distinct on (a.gg_name,a.href) a.*,b.ent_key,c.person_key from a left join "public".qy_base as b  on a.zhongbiaoren=b.jgmc 
     left join  public.t_person as c  on  a.xmjl=c.name and a.xmjl_zsbh=c.zjhm
    """%(quyu,max_html_key,quyu)


    db_command(sql1,dbtype="postgresql",conp=conp_gp)
    df=db_query("select max(html_key),count(*) from etl.gg_zhongbiao_%s "%quyu,dbtype="postgresql",conp=conp_gp)
    cnt=df.iat[0,1]
    print("etl.gg_zhongbiao_%s :此次更新数据 %d 条"%(quyu,cnt))
    max_html_key1=df.iat[0,0]

    return max_html_key1


#
def et_gg_zhongbiao_quyu(quyu,conp_gp,conp_app5):
    user,passwd,host,db,schema=conp_gp
    sql="""
    drop external table if exists cdc.et_gg_zhongbiao_anhui_anqing_ggzy;
    create  external table  cdc.et_gg_zhongbiao_anhui_anqing_ggzy(
    "html_key" int8,
    "href" text ,
    "ggtype" text ,
    "quyu" text ,
    "zhongbiaoren" text ,
    "zhaobiaoren" text ,
    "zbdl" text ,
    "zhongbiaojia" numeric,
    "kzj" numeric,
    "xmmc" text ,
    "xmjl" text ,
    "xmdz" text ,
    "zbfs" text ,
    "xmbh" text ,
    "gg_name" text ,
    "fabu_time" timestamp(6),
    "xzqh" text ,
    "ts_title" text,
    "ent_key" int8
    )
    LOCATION ('pxf://etl.gg_zhongbiao_anhui_anqing_ggzy?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/base_db&USER=%s&PASS=%s')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,user,passwd)

    sql=sql.replace("anhui_anqing_ggzy",quyu)

    db_command(sql,dbtype="postgresql",conp=conp_app5)


def insert_into(quyu,conp_gp,conp_app5):
    et_gg_zhongbiao_quyu(quyu,conp_gp,conp_app5)
    sql="""
    insert into "public".gg_zhongbiao( html_key,  href ,   ggtype , quyu ,   zhongbiaoren,    zhaobiaoren ,zbdl  ,  zhongbiaojia  ,  kzj, xmmc,    xmjl ,   xmdz ,
           zbfs  ,  xmbh ,   gg_name, fabu_time ,  xzqh ,   ts_title,ent_key)

    select html_key,  href ,   ggtype ,quyu ,   zhongbiaoren, zhaobiaoren ,zbdl  ,zhongbiaojia::numeric zhongbiaojia  
    ,  kzj, xmmc,  xmjl ,   xmdz ,zbfs  ,  xmbh , gg_name,fabu_time ,  xzqh , ts_title::tsvector as ts_tile,ent_key
     from cdc.et_gg_zhongbiao_%s 
    """%(quyu)
    db_command(sql,dbtype="postgresql",conp=conp_app5)





# quyu="anhui_anqing_ggzy"
# conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
# conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']
# pre_quyu_cdc(quyu,conp_gp)
#update(quyu,conp_gp,conp_app)