import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

import time 

def est_gg_zhongbiao(conp):
    sql="""
    CREATE  TABLE if not exists "public"."gg_zhongbiao" (
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
    "ts_title" tsvector,
    "ent_key" int8,
    "person_key" int8 
    )
    distributed by (html_key)"""

    db_command(sql,dbtype="postgresql",conp=conp)

def update_gg_zhongbiao(conp):
    bg=time.time()

    est_gg_zhongbiao(conp)
    sql="truncate table public.gg_zhongbiao;"
    db_command(sql,dbtype="postgresql",conp=conp)
    sql="""
    
    insert into public.gg_zhongbiao( html_key,  href ,   ggtype , quyu ,   zhongbiaoren,    zhaobiaoren ,zbdl  ,  zhongbiaojia  ,  kzj, xmmc,    xmjl ,xmjl_zsbh,   xmdz ,
           zbfs  ,  xmbh ,   gg_name, fabu_time ,  xzqh ,   ts_title,ent_key,person_key)

     with a as ( 
    select  html_key,  href ,   ggtype ,quyu ,   zhongbiaoren, zhaobiaoren ,zbdl  ,zhongbiaojia::numeric zhongbiaojia  
    ,  kzj, xmmc,  xmjl ,xmjl_zsbh,   xmdz ,zbfs  ,  xmbh , gg_name,fabu_time ,  xzqh , ts_title::tsvector ts_title 
        from public.gg_meta  as  t1 
    where   zhongbiaoren is not null  )


    select a.*,b.ent_key,c.person_key from a left join "public".qy_base as b  on a.zhongbiaoren=b.jgmc   left join  public.t_person as c  on  a.xmjl=c.name and a.xmjl_zsbh=c.zjhm
    """
    print(sql)

    db_command(sql,dbtype="postgresql",conp=conp)

    ed=time.time()

    cost=int(ed-bg)

    print("gg_zhongbiao 全表重导入耗时%s 秒"%cost)