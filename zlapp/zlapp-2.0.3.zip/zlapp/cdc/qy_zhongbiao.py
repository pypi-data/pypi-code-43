import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_qy_zhongbiao_quyu(quyu,conp_gp):
    sql="""
    CREATE  unlogged TABLE if not exists "etl"."qy_zhongbiao_%s" (
    zhongbiaoren text,
    gg_name text,
    fabu_time timestamp,
    html_key  bigint,
    zhongbiaojia numeric,
    ent_key bigint
    )
    distributed by (zhongbiaoren)"""%quyu
    db_command(sql,dbtype="postgresql",conp=conp_gp)

def pre_quyu_cdc(quyu,conp_gp):
    est_qy_zhongbiao_quyu(quyu,conp_gp)
    sql="truncate table etl.qy_zhongbiao_%s;"%quyu
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)

    sql1="""
    insert into etl.qy_zhongbiao_%s(zhongbiaoren  ,  gg_name ,fabu_time ,  html_key  ,  zhongbiaojia  ,  ent_key)
    with a as (SELECT zhongbiaoren
    ,gg_name 

    ,fabu_time 

    ,html_key

    ,zhongbiaojia 

     FROM "dst"."gg_meta"  where zhongbiaoren is not null and zhongbiaoren in (SELECT zhongbiaoren FROM "etl"."gg_zhongbiao_%s" )     )

    select a.*,b.ent_key  from a left join  "public".qy_base  as b on a.zhongbiaoren=b.jgmc

    """%(quyu,quyu)

    cnt=db_query("select count(*) from etl.qy_zhongbiao_%s "%quyu,dbtype="postgresql",conp=conp_gp).iat[0,0]
    print("etl.qy_zhongbiao_%s :此次更新数据 %d 条"%(quyu,cnt))
    db_command(sql1,dbtype="postgresql",conp=conp_gp)



#insert into
def et_qy_zhongbiao_quyu(quyu,conp_gp,conp_app5):
    user,passwd,host,db,schema=conp_gp
    sql="""
    drop external table if exists cdc.et_qy_zhongbiao_anhui_anqing_ggzy;
    create  external table  cdc.et_qy_zhongbiao_anhui_anqing_ggzy(
    zhongbiaoren text,
    gg_name text,
    fabu_time timestamp,
    html_key  bigint,
    zhongbiaojia numeric,
    ent_key bigint
    )
    LOCATION ('pxf://etl.qy_zhongbiao_anhui_anqing_ggzy?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/base_db&USER=%s&PASS=%s')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,user,passwd)

    sql=sql.replace("anhui_anqing_ggzy",quyu)

    db_command(sql,dbtype="postgresql",conp=conp_app5)


def insert_into(quyu,conp_gp,conp_app5):
    et_qy_zhongbiao_quyu(quyu,conp_gp,conp_app5)
    sql="""
    delete from public.qy_zhongbiao where zhongbiaoren in (select zhongbiaoren from cdc.et_qy_zhongbiao_%s )
    """%(quyu)
    db_command(sql,dbtype="postgresql",conp=conp_app5)


    sql="""insert into public.qy_zhongbiao(zhongbiaoren ,gg_names,gg_fabutimes,html_keys,zhongbiaojias,zhongbiao_counts,ent_key)
    select zhongbiaoren
   ,array_agg(gg_name order by fabu_time desc ) as gg_names 


    ,array_agg(fabu_time order by fabu_time desc) gg_fabutimes

    ,array_agg(html_key order by fabu_time desc) html_keys

    ,array_agg(zhongbiaojia order by fabu_time desc ) as zhongbiaojias 
    
    ,count(*) zhongbiao_counts
    ,(array_agg(ent_key  ))[1] as ent_key 
            from cdc.et_qy_zhongbiao_%s group by zhongbiaoren
    """%quyu
    db_command(sql,dbtype="postgresql",conp=conp_app5)



# quyu="anhui_anqing_ggzy"
# conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
# conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']