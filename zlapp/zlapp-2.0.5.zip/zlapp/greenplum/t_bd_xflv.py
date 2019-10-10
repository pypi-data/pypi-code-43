import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC,JSON
import time 
def est_t_bd_xflv(conp):
    sql="""
    CREATE  TABLE if not exists "public"."t_bd_xflv" (
    "bd_key" int8,
    "zbr" text COLLATE "default",
    "zhaobiao_time" timestamp(6),
    "zhongbiao_time" timestamp(6),
    "zhongbiaoren" text COLLATE "default",
    "kzj" float8,
    "zhongbiaojia" float8,
    "bd_bh" text COLLATE "default",
    "xzqh" text COLLATE "default",
    "gg_info" json,
    "xflv" numeric
    )distributed by(bd_key)
    """
    db_command(sql,dbtype="postgresql",conp=conp)



def update_t_bd_xflv_prt1(conp):
    sql="    truncate public.t_bd_xflv;"
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""
    insert into public.t_bd_xflv(bd_key ,zbr ,zhaobiao_time  , zhongbiao_time , zhongbiaoren  ,  kzj ,zhongbiaojia ,   bd_bh ,  xzqh ,   gg_info ,xflv)
    with   a as (select 
    bd_key
    ,(array_agg(info::jsonb->>'zbr'))[1] as zbr
    ,(array_agg(info::jsonb->>'zhongbiao_hxr'))[1] as zhongbiaoren
    ,(array_agg(info::jsonb->>'kzj'))[1] as kzj
    ,(array_agg(info::jsonb->>'zhongbiaojia'))[1] as zhongbiaojia
    ,(array_agg(info::jsonb->>'bd_bh'))[1] as bd_bh

    ,(array_agg(xzqh))[1] as xzqh
    ,array_to_json(array_agg(json_build_object('html_key',html_key,'ggtype',ggtype,'gg_name',gg_name,'fabu_time',fabu_time) order by fabu_time desc) ) as gg_info
    ,(array_agg(fabu_time order by fabu_time asc)  )[1] zhaobiao_time
    ,(array_agg(fabu_time order by fabu_time desc) )[1] zhongbiao_time

     from public.gg where quyu~'zlsys'  
    group by bd_key )

    ,b as(

    select *,  1-(zhongbiaojia::float)/(kzj::float) as xflv from a where kzj is not null and kzj::float>0 and zhongbiaojia is not null )

    select bd_key   ,zbr,zhaobiao_time,zhongbiao_time,  zhongbiaoren,   kzj::float kzj  ,
    zhongbiaojia::float zhongbiaojia,   bd_bh,  xzqh,   gg_info,  case when round(xflv::numeric,4)<0 then 0 else round(xflv::numeric,4) end as xflv 

    from b
    """
    print(sql)

    db_command(sql,dbtype="postgresql",conp=conp)


def update_t_bd_xflv(conp):
    bg=time.time()
    est_t_bd_xflv(conp)
    update_t_bd_xflv_prt1(conp)

    ed=time.time()
    cost=int(ed-bg)
    print("t_bd_xflv全表更新，需要耗时%d"%cost)

    # print("同步t_bd_xflv全表更新，需要耗时")
    # conp_app=["gpadmin","since2015",'192.168.4.206','biaost',"public"]
    # conp_pg=["postgres","since2015",'192.168.4.207','biaost',"public"]
    # datadict={"bd_key":BIGINT(),"zbr":TEXT(), "zhaobiao_time":TIMESTAMP(),"zhongbiao_time":TIMESTAMP(),"zhongbiaoren":TEXT(),
    # "kzj":NUMERIC(), "zhongbiaojia":NUMERIC(),"bd_bh":TEXT(),"xzqh":TEXT(),"gg_info":JSON(),"xflv":NUMERIC()}
 
    # pg2pg("select * from t_bd_xflv",'t_bd_xflv',conp_app,conp_pg,datadict=datadict,chunksize=2000)
