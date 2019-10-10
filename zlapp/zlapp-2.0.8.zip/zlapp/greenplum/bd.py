import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC


def est_bd(conp):
    sql="""
    CREATE  TABLE if not exists "public"."bd" (
    "bd_key" int8,
    "bd_guid" text COLLATE "default",
    "bd_name" text COLLATE "default",
    "bd_bh" text COLLATE "default",
    "zhaobiaoren" text COLLATE "default",
    "zbdl" text COLLATE "default",
    "kzj" numeric,
    "xm_name" text COLLATE "default",
    "fabu_time" timestamp(6),
    "quyu" text COLLATE "default",
    "xzqh" text COLLATE "default"
    )
    DISTRIBUTED REPLICATED
  

    """
    db_command(sql,dbtype="postgresql",conp=conp)

def update_bd(conp):
    est_bd(conp)

    sql="""    truncate table "public".bd;"""
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""
    insert into public.bd (bd_key ,  bd_guid ,bd_name ,bd_bh ,  zhaobiaoren ,zbdl   , xm_name, kzj ,fabu_time,  quyu   , xzqh)
        SELECT
        distinct on(bd_key)
         bd_key
        ,info::json->>'bd_guid' as bd_guid 
        ,info::json->>'bd_name' as bd_name
        ,info::json->>'bd_bh' as bd_bh
        ,info::json->>'zbr' as zhaobiaoren
        ,info::json->>'zbdl' as zbdl  
        ,info::json->>'xm_name' as xm_name
        ,(info::json->>'kzj')::float as kzj
        ,fabu_time 
        ,quyu ,xzqh  
        FROM "public"."gg_meta" where quyu~'zlsys' order by bd_key ,fabu_time  asc;
        """
    print(sql)

    db_command(sql,dbtype="postgresql",conp=conp)