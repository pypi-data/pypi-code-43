import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_xmjl_zhongbiao_quyu(quyu,conp_gp):
    sql="""
    CREATE  unlogged TABLE if not exists "etl"."xmjl_zhongbiao_%s" (
    zxmjl text,
    gg_name text,
    fabu_time timestamp,
    html_key  bigint,
    zhongbiaojia numeric,
    person_key bigint
    )
    distributed by (person_key)"""%quyu
    db_command(sql,dbtype="postgresql",conp=conp_gp)

def pre_quyu_cdc(quyu,conp_gp):
    est_xmjl_zhongbiao_quyu(quyu,conp_gp)
    sql="truncate table etl.xmjl_zhongbiao_%s;"%quyu
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)

    sql1="""
    insert into etl.xmjl_zhongbiao_%s(xmjl  ,  gg_name ,fabu_time ,  html_key  ,  zhongbiaojia  ,  person_key)
    with a as (SELECT xmjl
    ,gg_name 

    ,fabu_time 

    ,html_key

    ,zhongbiaojia 

     FROM "dst"."gg_meta"  as t1 where  exists (SELECT 1 FROM "etl"."gg_zhongbiao_%s" as t2 where t2.person_key is not null and t1.xmjl=t2.xmjl and t1.xmjl_zsbh=t2.xmjl_zsbh )     )

    select a.*,b.person_key  from a left join  "public".t_person  as b on a.xmjl_zsbh=b.xmjl_zsbh and a.xmjl=b.xmjl
    """%(quyu,quyu)

    cnt=db_query("select count(*) from etl.qy_zhongbiao_%s "%quyu,dbtype="postgresql",conp=conp_gp).iat[0,0]
    print("etl.qy_zhongbiao_%s :此次更新数据 %d 条"%(quyu,cnt))
    db_command(sql1,dbtype="postgresql",conp=conp_gp)

def et_qy_zhongbiao_quyu(quyu,conp_app):

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
    LOCATION ('pxf://etl.qy_zhongbiao_anhui_anqing_ggzy?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.183:5433/base_db&USER=gpadmin&PASS=since2015')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """

    sql=sql.replace("anhui_anqing_ggzy",quyu)

    db_command(sql,dbtype="postgresql",conp=conp_app)


def insert_into(quyu,conp_app):
    et_qy_zhongbiao_quyu(quyu,conp_app)
    sql="""
    delete from public.qy_zhongbiao where zhongbiaoren in (select zhongbiaoren from cdc.et_qy_zhongbiao_%s )
    """%(quyu)
    db_command(sql,dbtype="postgresql",conp=conp_app)


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
    db_command(sql,dbtype="postgresql",conp=conp_app)


def update(quyu,conp_gp,conp_app):
    print("----------------------%s 开始更新--------------------------------------- "%quyu)
    pre_qy_zhongbiao(quyu,conp_gp)
    insert_into(quyu,conp_app)


# quyu="anhui_anqing_ggzy"
# conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
# conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']