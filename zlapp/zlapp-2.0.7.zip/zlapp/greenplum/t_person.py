import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_t_person(conp_app5):
    sql="""
    CREATE TABLE if not exists "public"."t_person" (
    "person_key" bigint primary key  ,
    "name" text COLLATE "default" NOT NULL,
    "zj_type" text COLLATE "default",
    "zjhm" text COLLATE "default" NOT NULL
    )
    distributed by (person_key)

    """



    db_command(sql,dbtype="postgresql",conp=conp_app5)



def update_t_person(conp_app5):
    est_t_person(conp_app5)
    sql="""
    truncate public.t_person;
    insert into "public".t_person(person_key,   name,   zj_type,    zjhm)


    select * from "public".et_t_person 
    """
    print(sql)


    db_command(sql,dbtype="postgresql",conp=conp_app5)