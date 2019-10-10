import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_app_qy_zz_quyu(quyu,conp_gp):
    sql="""
    CREATE unlogged TABLE if not exists "etl"."app_qy_zz_%s" (
    "ent_key" int8,
    "entname" text ,
    "zzlb" text ,
    "zzmc" text ,
    "zzbh" text ,
    "zzcode" text ,
    "xzqh" text ,
    "fddbr" text ,
    "alias" text ,
    "clrq" timestamp(6),
    "zczj" text ,
    "logo" text ,
    "qy_alias" text ,
    "fabu_time" timestamp(6),
    "total" int8
    )
    distributed by (ent_key)"""%quyu
    db_command(sql,dbtype="postgresql",conp=conp_gp)

def pre_quyu_cdc(quyu,conp_gp):
    est_app_qy_zz_quyu(quyu,conp_gp)
    sql="truncate table etl.app_qy_zz_%s;"%quyu
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)
    sql1="""
    insert into etl.app_qy_zz_%s(ent_key    ,entname ,zzlb   , zzmc  ,  zzbh   , zzcode , xzqh    ,fddbr  , alias  , clrq ,   zczj   , logo  ,  qy_alias ,   fabu_time  , total)
    with a as (SELECT  ent_key, entname,zzlb,zzmc,zzbh,zzcode,xzqh,fddbr,alias  FROM "etl"."qy_zz" where ent_key is not null )
    

    ,c as (select zhongbiaoren,max(fabu_time) fabu_time,count(*) zhongbiao_counts from etl.qy_zhongbiao_%s group by zhongbiaoren )
        
        ,b as (select jgmc,clrq,zczj,logo,alias as qy_alias from public.qy_base)

    select 
    a.*,b.clrq,b.zczj,b.logo,b.qy_alias
    ,coalesce(c.fabu_time,'1900-01-01'::timestamp(0)) as fabu_time
    ,coalesce(c.zhongbiao_counts,0) as total 

    from a left join b on a.entname=b.jgmc inner join c  on a.entname=c.zhongbiaoren  
    """%(quyu,quyu)

    db_command(sql1,dbtype="postgresql",conp=conp_gp)

    cnt=db_query("select count(*) from etl.app_qy_zz_%s "%quyu,dbtype="postgresql",conp=conp_gp).iat[0,0]
    print("etl.app_qy_zz_%s :此次更新数据 %d 条"%(quyu,cnt))



def et_app_qy_zz_quyu(quyu,conp_gp,conp_app5):
    user,passwd,host,db,schema=conp_gp
    sql="""
    drop external table if exists cdc.et_app_qy_zz_anhui_anqing_ggzy;
    create  external table  cdc.et_app_qy_zz_anhui_anqing_ggzy(
    "ent_key" int8,
    "entname" text ,
    "zzlb" text ,
    "zzmc" text ,
    "zzbh" text ,
    "zzcode" text ,
    "xzqh" text ,
    "fddbr" text ,
    "alias" text ,
    "clrq" timestamp(6),
    "zczj" text ,
    "logo" text ,
    "qy_alias" text ,
    "fabu_time" timestamp(6),
    "total" int8
    )
    LOCATION ('pxf://etl.app_qy_zz_anhui_anqing_ggzy?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/base_db&USER=%s&PASS=%s')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,user,passwd)


    sql=sql.replace("anhui_anqing_ggzy",quyu)

    db_command(sql,dbtype="postgresql",conp=conp_app5)


def insert_into(quyu,conp_gp,conp_app5):
    et_app_qy_zz_quyu(quyu,conp_gp,conp_app5)
    sql="""
    delete from public.app_qy_zz where ent_key in (select ent_key from cdc.et_app_qy_zz_%s )
    """%(quyu)
    db_command(sql,dbtype="postgresql",conp=conp_app5)


    sql="""insert into public.app_qy_zz(ent_key ,entname, zzlb  ,  zzmc   , zzbh   , zzcode , xzqh  ,  fddbr  , alias  , clrq   , zczj   , logo  ,  qy_alias  ,  fabu_time  , total)
    select 
    ent_key ,entname, zzlb  ,  zzmc   , zzbh   , zzcode , xzqh  ,  fddbr  , alias  , clrq   , zczj   , logo  ,  qy_alias  ,  fabu_time  , total
            from cdc.et_app_qy_zz_%s 
    """%quyu
    db_command(sql,dbtype="postgresql",conp=conp_app5)





# quyu="anhui_anqing_ggzy"
# conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
# conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']