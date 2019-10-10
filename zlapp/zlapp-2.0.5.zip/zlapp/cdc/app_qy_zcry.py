import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_app_qy_zcry_quyu(quyu,conp_gp):
    sql="""
    CREATE unlogged TABLE if not exists "etl"."app_qy_zcry_%s" (
    "ent_key" int8,
    "tydm" text ,
    "xzqh" text ,
    "ryzz_code" text ,
    "href" text ,
    "name" text ,
    "gender" text ,
    "zjhm" text ,
    "zj_type" text ,
    "zclb" text ,
    "zhuanye" text ,
    "zsbh" text,
    "yzh" text ,
    "youxiao_date" text,
    "entname" text,
    "person_key" int8,
    "total" int8,
    "fabu_time" timestamp(6),
    "zczj" text ,
    "fddbr" text ,
    "clrq" timestamp(6),
    "qy_alias" text ,
    "logo" text 

    )
    distributed by (ent_key)"""%quyu
    db_command(sql,dbtype="postgresql",conp=conp_gp)
def pre_quyu_cdc(quyu,conp_gp):
    est_app_qy_zcry_quyu(quyu,conp_gp)
    sql="truncate table etl.app_qy_zcry_%s;"%quyu
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)

    sql1="""
  
    insert into etl.app_qy_zcry_%s(ent_key,   tydm,   xzqh    ,ryzz_code  ,href,  name,   gender  ,zjhm   ,zj_type,   zclb    ,zhuanye,   zsbh    ,yzh,   youxiao_date,   entname
        ,person_key ,total  ,fabu_time  ,zczj   
    ,fddbr  ,clrq   ,qy_alias   ,logo)
    SELECT 
    a.*

    ,b.zhongbiao_counts as total 
    ,b.fabu_time 

    ,d.zczj
    ,d.fddbr
    ,d.clrq
    ,a1.alias as qy_alias
    ,a1.logo
    FROM "public"."qy_zcry" as a left join "public".qy_base as a1
    on a.ent_key=a1.ent_key 
    inner join 
        (select zhongbiaoren,max(fabu_time) fabu_time,count(*) zhongbiao_counts from etl.qy_zhongbiao_%s group by zhongbiaoren ) as b
                on a.entname=b.zhongbiaoren
    left join public.t_person as c on a.name=c.name and a.zjhm=c.zjhm
    left join public.qy_base as d on a.entname=d.jgmc
     ;
    """%(quyu,quyu)

    db_command(sql1,dbtype="postgresql",conp=conp_gp)
    cnt=db_query("select count(*) from etl.app_qy_zcry_%s "%quyu,dbtype="postgresql",conp=conp_gp).iat[0,0]
    print("etl.app_qy_zcry_%s :此次更新数据 %d 条"%(quyu,cnt))






def et_app_qy_zcry_quyu(quyu,conp_gp,conp_app5):
    user,passwd,host,db,schema=conp_gp

    sql="""
    drop external table if exists cdc.et_app_qy_zcry_anhui_anqing_ggzy;
    create  external table  cdc.et_app_qy_zcry_anhui_anqing_ggzy(
    "ent_key" int8,
    "tydm" text ,
    "xzqh" text ,
    "ryzz_code" text ,
    "href" text ,
    "name" text ,
    "gender" text ,
    "zjhm" text ,
    "zj_type" text ,
    "zclb" text ,
    "zhuanye" text ,
    "zsbh" text,
    "yzh" text ,
    "youxiao_date" text,
    "entname" text,
    "person_key" int8,
    "total" int8,
    "fabu_time" timestamp(6),
    "zczj" text ,
    "fddbr" text ,
    "clrq" timestamp(6),
    "qy_alias" text ,
    "logo" text 
    )
    LOCATION ('pxf://etl.app_qy_zcry_anhui_anqing_ggzy?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/base_db&USER=%s&PASS=%s')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,user,passwd)


    sql=sql.replace("anhui_anqing_ggzy",quyu)

    db_command(sql,dbtype="postgresql",conp=conp_app5)


def insert_into(quyu,conp_gp,conp_app5):
    et_app_qy_zcry_quyu(quyu,conp_gp,conp_app5)
    sql="""
    delete from public.app_qy_zcry where ent_key in (select ent_key from cdc.et_app_qy_zcry_%s )
    """%(quyu)
    db_command(sql,dbtype="postgresql",conp=conp_app5)


    sql="""insert into public.app_qy_zcry(ent_key,   tydm,   xzqh    ,ryzz_code  ,href,  name,   gender  ,zjhm   ,zj_type,   zclb    ,zhuanye,   zsbh    ,yzh,   youxiao_date,   entname
        ,person_key ,total  ,fabu_time  ,zczj   
    ,fddbr  ,clrq   ,qy_alias   ,logo)
    select 
    ent_key,   tydm,   xzqh    ,ryzz_code  ,href,  name,   gender  ,zjhm   ,zj_type,   zclb    ,zhuanye,   zsbh    ,yzh,   youxiao_date,   entname
        ,person_key ,total  ,fabu_time  ,zczj   
    ,fddbr  ,clrq   ,qy_alias   ,logo
            from cdc.et_app_qy_zcry_%s 
    """%quyu
    db_command(sql,dbtype="postgresql",conp=conp_app5)






# quyu="anhui_anqing_ggzy"
# conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
# conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']