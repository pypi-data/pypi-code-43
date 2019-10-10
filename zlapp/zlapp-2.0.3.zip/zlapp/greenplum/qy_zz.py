import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC






def est_qy_zz(conp_app5):
    sql="""
    CREATE TABLE if not exists "public"."qy_zz" (
    "href" text COLLATE "default",
    "zzbh" text COLLATE "default",
    "gsd" text COLLATE "default",
    "jglx" text COLLATE "default",
    "zzmc" text COLLATE "default",
    "bgdate" text COLLATE "default",
    "eddate" text COLLATE "default",
    "fbjg" text COLLATE "default",
    "tydm" text COLLATE "default",
    "fddbr" text COLLATE "default",
    "zzlb" text COLLATE "default",
    "entname" text COLLATE "default",
    "jgdz" text COLLATE "default",
    "qita" text COLLATE "default",
    "ent_key" int8,
    "xzqh" text COLLATE "default",
    "zzcode" text COLLATE "default",
    "alias" text COLLATE "default"
    )
    distributed by (ent_key)

    """



    db_command(sql,dbtype="postgresql",conp=conp_app5)

def update_qy_zz(conp_app5):
    est_qy_zz(conp_app5)
    sql="""
    truncate table "public".qy_zz;
    insert into "public".qy_zz(href,    zzbh,   gsd ,jglx,  zzmc,   bgdate, eddate  ,fbjg,  tydm,   fddbr   ,zzlb,  entname,    jgdz,   qita    ,ent_key,   xzqh    ,zzcode ,alias)
    SELECT href,    zzbh,   gsd ,jglx,  zzmc,   bgdate, eddate  ,fbjg,  tydm,   fddbr   ,zzlb,  entname,    jgdz,   qita    ,ent_key,   xzqh    ,zzcode ,alias   FROM "public"."et_qy_zz";
        """
    print(sql)


    db_command(sql,dbtype="postgresql",conp=conp_app5)