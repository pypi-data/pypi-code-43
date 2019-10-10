import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time 
def est_app_qy_zz(conp):
    sql="""
    CREATE  TABLE if not exists "public"."app_qy_zz" (
    "ent_key" int8,
    "entname" text COLLATE "default",
    "zzlb" text COLLATE "default",
    "zzmc" text COLLATE "default",
    "zzbh" text COLLATE "default",
    "zzcode" text COLLATE "default",
    "xzqh" text COLLATE "default",
    "fddbr" text COLLATE "default",
    "alias" text COLLATE "default",
    "clrq" timestamp(6),
    "zczj" text COLLATE "default",
    "logo" text COLLATE "default",
    "qy_alias" text COLLATE "default",
    "fabu_time" timestamp(6),
    "total" int8
    )
    distributed by (ent_key )"""

    db_command(sql,dbtype="postgresql",conp=conp)



def update_app_qy_zz(conp):
    bg=time.time()
    est_app_qy_zz(conp)
    sql="truncate public.app_qy_zz;"
    db_command(sql,dbtype="postgresql",conp=conp)
    sql="""
    
    insert into "public".app_qy_zz(ent_key, entname,    zzlb,   zzmc,   zzbh    ,zzcode,    xzqh,   fddbr   ,alias, clrq,   zczj,   logo    ,qy_alias,  fabu_time,  total) 
    
    with a as (SELECT  ent_key, entname,zzlb,zzmc,zzbh,zzcode,xzqh,fddbr,alias  FROM "public"."qy_zz" where ent_key is not null )
    ,b as (select jgmc,clrq,zczj,logo,alias as qy_alias from public.qy_base)

    ,c as (select zhongbiaoren,gg_fabutimes[1] as fabu_time,zhongbiao_counts from public.qy_zhongbiao )

    select 
    a.*,b.clrq,b.zczj,b.logo,b.qy_alias
    ,coalesce(c.fabu_time,'1900-01-01'::timestamp(0)) as fabu_time
    ,coalesce(c.zhongbiao_counts,0) as total 

    from a left join b on a.entname=b.jgmc left join c  on a.entname=c.zhongbiaoren  
    """
    print(sql)


    db_command(sql,dbtype="postgresql",conp=conp)
    ed=time.time()
    cost=int(ed-bg)
    print("app_qy_zz 耗时%s"%cost)