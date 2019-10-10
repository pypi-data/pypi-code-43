import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time 
def est_xmjl_zhongbiao(conp):
    sql="""
    CREATE  TABLE if not exists "public"."xmjl_zhongbiao" (
    "xmjl" text COLLATE "default",
    "gg_names" _text,
    "gg_fabutimes" _timestamp,
    "html_keys" _int8,
    "zhongbiaojias" _numeric,
    "zhongbiao_counts" int8,
    "person_key" int8
    ) distributed by (person_key)"""

    db_command(sql,dbtype="postgresql",conp=conp)



def update_xmjl_zhongbiao(conp):
    bg=time.time()
    est_xmjl_zhongbiao(conp)
    sql="""    truncate  public.xmjl_zhongbiao;"""
    db_command(sql,dbtype="postgresql",conp=conp)
    sql="""
    insert into public.xmjl_zhongbiao(xmjl,   gg_names,   gg_fabutimes,   html_keys,  zhongbiaojias,  zhongbiao_counts,   person_key)


    with a as (SELECT (array_agg(xmjl order by fabu_time desc ))[1] as xmjl 
    ,array_agg(gg_name order by fabu_time desc ) as gg_names 


    ,array_agg(fabu_time order by fabu_time desc) gg_fabutimes

    ,array_agg(html_key order by fabu_time desc) html_keys

    ,array_agg(zhongbiaojia order by fabu_time desc ) as zhongbiaojias 
    
    ,count(*) zhongbiao_counts
    
    , person_key 


     FROM "public"."gg_zhongbiao" where person_key is not null  group by person_key )


    select * from a 

 
    """
    #select a.*,b.ent_key from a left join  "public".qy_base  as b on a.zhongbiaoren=b.jgmc 
    print(sql)


    db_command(sql,dbtype="postgresql",conp=conp)

    ed=time.time()
    cost=int(ed-bg)
    print("xmjl_zhongbiao表更新需要 %s "%cost)