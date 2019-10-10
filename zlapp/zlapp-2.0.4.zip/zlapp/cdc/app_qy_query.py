import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_app_qy_query_quyu(quyu,conp_gp):
    sql="""
    CREATE unlogged TABLE if not exists "etl"."app_qy_query_%s" (
    "html_key" int8,
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
    distributed by (ent_key)"""%quyu
    db_command(sql,dbtype="postgresql",conp=conp_gp)

def pre_quyu_cdc(quyu,conp_gp):
    est_app_qy_query_quyu(quyu,conp_gp)
    sql="truncate table etl.app_qy_query_%s;"%quyu
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)
    sql1="""
    create temp table a_ as 
     select a1.* from dst.gg_meta as a1  ,etl.gg_meta_anhui_anqing_ggzy as a2 where a1.person=a2.zhongbiaoren  and a1.person is not null 

    union  
    select a1.* from dst.gg_meta as a1  ,etl.gg_meta_anhui_anqing_ggzy as a2 where a1.person=a2.zhaobiaoren and a1.person is not null

    union  

    select a1.* from dst.gg_meta as a1  ,etl.gg_meta_anhui_anqing_ggzy as a2 where a1.person=a2.zbdl and a1.person is not null
    ;

    insert into etl.app_qy_query_anhui_anqing_ggzy(html_key ,   href  ,  ggtype , quyu  ,  entname ,entrole ,price  , diqu  ,  xzqh  ,  fabu_time ,  gg_name, ent_key)


        with a as (SELECT html_key,href,ggtype,quyu
        ,zhongbiaoren as entname ,'中标人'::text entrole
        ,zhongbiaojia::float as price  ,diqu,xzqh,fabu_time,gg_name
         FROM a_  where zhongbiaoren is not null  )

         
        ,b as (SELECT html_key,href,ggtype,quyu
        ,zhaobiaoren as entname ,'招标人'::text entrole
        ,kzj::float as price  ,diqu,xzqh,fabu_time,gg_name
         FROM a_ where zhaobiaoren is not null 
         )
         
        ,c as (SELECT html_key,href,ggtype,quyu
        ,zbdl as entname ,'招标代理'::text entrole
        ,kzj::float as price  ,diqu,xzqh,fabu_time,gg_name
         FROM a_  where zbdl is not null )
         
        , d as (
         select * from a union  select * from b union select * from c)
    select  d.*,ent_key from d  left join public.qy_base as e  on d.entname=e.jgmc  
    """
    sql1=sql1.replace('anhui_anqing_ggzy',quyu)

    db_command(sql1,dbtype="postgresql",conp=conp_gp)

    cnt=db_query("select count(*) from etl.app_qy_query_%s "%quyu,dbtype="postgresql",conp=conp_gp).iat[0,0]
    print("etl.app_qy_query_%s :此次更新数据 %d 条"%(quyu,cnt))

def et_app_qy_query_quyu(quyu,conp_gp,conp_app5):
    user,passwd,host,db,schema=conp_gp
    sql="""
    drop external table if exists cdc.et_app_qy_query_anhui_anqing_ggzy;
    create  external table  cdc.et_app_qy_query_anhui_anqing_ggzy(
    "html_key" int8,
    "href" text,
    "ggtype" text,
    "quyu" text ,
    "entname" text,
    "entrole" text ,
    "price" numeric,
    "diqu" text ,
    "xzqh" text ,
    "fabu_time" timestamp(6),
    "gg_name" text ,
    "ent_key" int8
    )
    LOCATION ('pxf://etl.app_qy_query_anhui_anqing_ggzy?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/base_db&USER=%s&PASS=%s')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,user,passwd)

    sql=sql.replace("anhui_anqing_ggzy",quyu)

    db_command(sql,dbtype="postgresql",conp=conp_app5)




def insert_into(quyu,conp_gp,conp_app5):
    et_app_qy_query_quyu(quyu,conp_gp,conp_app5)
    sql="""
    delete from public.app_qy_query where ent_key in (select ent_key from cdc.et_app_qy_query_%s )
    """%(quyu)
    db_command(sql,dbtype="postgresql",conp=conp_app5)


    sql="""insert into public.app_qy_query(ent_key , entname, fddbr,   clrq ,   zczj ,   xzqh ,   qy_alias ,logo,   zhongbiaodate_latest,    zhongbiao_counts   
     ,qy_zz_codes ,qy_zz_info  ,ry_zz_codes ,ry_zz_info , gg_info    ,latest_gg_fabu_time
    ,gg_info_length)

    with e as (SELECT ent_key,jgmc as entname,fddbr,clrq,zczj,xzqh,alias as qy_alias,logo FROM "public"."qy_base" )

    ,b as (select ent_key,max(fabu_time) as zhongbiaodate_latest,count(*) zhongbiao_counts 
    from cdc.et_qy_zhongbiao_anhui_anqing_ggzy where ent_key is not null group by ent_key )



    ,c as (SELECT ent_key, array_agg(zzmc) as qy_zz_info,string_agg('code-'||zzcode,',') as qy_zz_codes

     FROM "cdc"."et_app_qy_zz_anhui_anqing_ggzy" where ent_key is not null group by ent_key)

    ,d as (
    select ent_key
    , array_agg(json_build_object( 'person_name',name,'person_key',person_key,'zzmc',concat(zclb,'-',zhuanye)
    ,'currentTotal','','currentDate','' ) order by youxiao_date,name ) as ry_zz_info
    ,string_agg('code-'||ryzz_code,',') ry_zz_codes
     from cdc.et_app_qy_zcry_anhui_anqing_ggzy where ent_key is not null 

    group by ent_key 
    )

    ,a as (
    SELECT 
    ent_key, 
    array_agg(  json_build_object('html_key', html_key,'gg_name',gg_name,'gg_type',ggtype,'fabu_time',fabu_time,'price',price)  order by fabu_time desc ,gg_name ) gg_info

    ,max(fabu_time) as latest_gg_fabu_time
    ,count(html_key) as gg_info_length

     FROM "cdc"."et_app_qy_query_anhui_anqing_ggzy" 
    where ent_key is not null

    group by ent_key)

    select e.* ,b.zhongbiaodate_latest,b.zhongbiao_counts 
    ,c.qy_zz_codes
    ,c.qy_zz_info
    ,d.ry_zz_codes
    ,d.ry_zz_info
    ,a.gg_info 
    ,a.latest_gg_fabu_time
    ,a.gg_info_length


    from a left join b on a.ent_key=b.ent_key 
    left join c on a.ent_key=c.ent_key 
    left join d on a.ent_key=d.ent_key 
    left join e on a.ent_key=e.ent_key   
    """
    sql=sql.replace("anhui_anqing_ggzy",quyu)
    db_command(sql,dbtype="postgresql",conp=conp_app5)



# quyu="anhui_anqing_ggzy"
# conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
# conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']