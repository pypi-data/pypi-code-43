import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time 

def est_gg(conp):
    sql="""
    CREATE TABLE if not exists "public"."gg" (
    "html_key" bigint NOT NULL,
    "guid" text COLLATE "default",
    "gg_name" text COLLATE "default",
    "href" text COLLATE "default",
    "fabu_time" timestamp(6),
    "ggtype" text COLLATE "default",
    "jytype" text COLLATE "default",
    "diqu" text COLLATE "default",
    "quyu" text COLLATE "default",
    "info" text COLLATE "default",
    "create_time" timestamp(6),
    "xzqh" text COLLATE "default",
    "ts_title" tsvector,
    "bd_key" int8,
    "person" text COLLATE "default",
    "price" numeric
    ) distributed by(html_key)

    PARTITION BY RANGE (fabu_time) 
    (partition gg_prt_other start ('1800-01-01'::date) end ('2019-01-01'::date) ,
    partition gg_prt_normal start ('2019-01-01'::date) end ('2020-01-01'::date) 
     )"""
    db_command(sql,dbtype="postgresql",conp=conp)

def update_gg(conp):
    est_gg(conp)
    bg=time.time()
    sql="truncate table public.gg;"
    db_command(sql,dbtype="postgresql",conp=conp)
    sql="""
    
    insert into gg(html_key,    guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu    ,quyu   ,info   ,create_time,   xzqh,   ts_title    ,bd_key ,person ,price) 

    select html_key,    guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu    ,quyu   ,info   
    ,create_time,   xzqh,   ts_title::tsvector as ts_title  ,bd_key ,person ,price::numeric as price from public.gg_meta as a where fabu_time>='1900-01-01' and fabu_time<'2020-01-01'
 
    """
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp)

    ed=time.time()
    cost=int(ed-bg)
    print("gg表全表重导 耗时 %s 秒"%cost)