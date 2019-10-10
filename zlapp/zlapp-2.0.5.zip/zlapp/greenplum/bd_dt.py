import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC


def est_bd_dt(conp):
    sql="""
    create  table if not exists public.bd_dt(
    html_key bigint ,
    guid text ,
    bd_key bigint,
    gg_name text ,
    ggtype text, 
    fabu_time timestamp, 
    gg_info text ,
    href text ,
    xzqh text ,
    create_time timestamp
    )
    distributed by (html_key)

    """
    db_command(sql,dbtype="postgresql",conp=conp)


def update_bd_dt(conp):

    est_bd_dt(conp)
    sql="truncate public.bd_dt;"
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""
    insert into public.bd_dt(html_key,    guid,   bd_key  ,gg_name,   ggtype, fabu_time   , gg_info, href ,xzqh, create_time)
    select html_key,    guid,   bd_key  ,gg_name,   ggtype, fabu_time   ,info as gg_info,href ,xzqh,   create_time
    
    from public.gg  as a  where quyu~'^zlsys' 
    
    """
    #and not exists(select 1 from bd_dt as b  where  a.html_key=b.html_key)
    print(sql)

    db_command(sql,dbtype="postgresql",conp=conp)

    # print("同步bd_dt表至207")
    # conp_app=["gpadmin","since2015",'192.168.4.206','biaost',"public"]
    # conp_pg=["postgres","since2015",'192.168.4.207','biaost',"public"]
    # datadict={"html_key":BIGINT(),"guid":TEXT(),"bd_key":BIGINT(),"gg_name":TEXT(),"ggtype":TEXT(),"fabu_time":TIMESTAMP(),"gg_info":TEXT(),"xzqh":TEXT(),"create_time":TIMESTAMP()}
    # pg2pg("select * from bd_dt",'bd_dt',conp_app,conp_pg,datadict=datadict,chunksize=10000)




# conp_app=["gpadmin","since2015",'192.168.4.206','biaost',"public"]
# conp_pg=["postgres","since2015",'192.168.4.207','biaost',"public"]

# datadict={"bd_key":BIGINT(),'fabu_time':TIMESTAMP()}

# pg2pg('select * from public.bd ','bd',conp_app,conp_pg,chunksize=10000,datadict=datadict)