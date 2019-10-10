import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time 

def est_gg_quyu(quyu,conp_gp):
    sql="""
    CREATE unlogged TABLE if not exists etl.gg_%s (
    html_key bigint,
    guid text,
    gg_name text,
    href text,
    fabu_time timestamp,
    ggtype text,
    jytype text,
    diqu text,
    quyu text,
    info text,
    create_time timestamp,
    xzqh text,
    ts_title text,
    bd_key bigint,
    person text,
    price text
    )
    distributed by(html_key)
    """%(quyu)
    db_command(sql,dbtype='postgresql',conp=conp_gp)


def get_max_html_key(quyu,conp_gp):
    max_html_key=db_query("select max_gg from etlmeta.t_html_key where quyu='%s'"%quyu,dbtype="postgresql",conp=conp_gp).iat[0,0]

    return max_html_key


def pre_quyu_cdc(quyu,conp_gp):
    max_html_key=get_max_html_key(quyu,conp_gp)
    print("gg 更新前最大html_key :",max_html_key)
    est_gg_quyu(quyu,conp_gp)
    
    sql="truncate table etl.gg_%s;"%quyu
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)

    sql1="""insert into etl.gg_%s(html_key, guid,gg_name,href,   fabu_time,  ggtype, jytype, diqu    ,quyu   ,info   ,create_time,   xzqh,   ts_title 
    ,bd_key ,person ,price) 
     select distinct on (gg_name,href) html_key,    guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu    ,quyu   ,info   
    ,create_time,   xzqh,   ts_title  ,bd_key ,person ,price from dst.gg_meta where quyu='%s' and html_key>%d 
    and  fabu_time>'1900-01-01' and fabu_time<'2020-01-01'  """%(quyu,quyu,max_html_key)

    db_command(sql1,dbtype="postgresql",conp=conp_gp)
    df=db_query("select max(html_key),count(*) from etl.gg_%s "%quyu,dbtype="postgresql",conp=conp_gp)
    cnt=df.iat[0,1]
    print("etl.gg_%s :此次更新数据 %d 条"%(quyu,cnt))
    max_html_key1=df.iat[0,0]

    return max_html_key1


###
def et_gg_quyu(quyu,conp_gp,conp_app5):
    user,passwd,host,db,schema=conp_gp
    sql="""
    drop external table if exists cdc.et_gg_anhui_anqing_ggzy;
    create  external table  cdc.et_gg_anhui_anqing_ggzy(html_key bigint,
    guid text,
    gg_name text,
    href text,
    fabu_time timestamp,
    ggtype text,
    jytype text,
    diqu text,
    quyu text,
    info text,
    create_time timestamp,
    xzqh text,
    ts_title text,
    bd_key bigint,
    person text,
    price text
    )
    LOCATION ('pxf://etl.gg_anhui_anqing_ggzy?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://%s/base_db&USER=%s&PASS=%s')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """%(host,user,passwd)

    sql=sql.replace("anhui_anqing_ggzy",quyu)

    db_command(sql,dbtype="postgresql",conp=conp_app5)


def insert_into(quyu,conp_gp,conp_app5):
    et_gg_quyu(quyu,conp_gp,conp_app5)
    sql="""
    insert into "public".gg(html_key,  guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu    ,quyu   ,info   ,create_time,   xzqh,
       ts_title    ,bd_key ,person ,price
   ) 

    select html_key,    guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu    ,quyu   ,info   
    ,create_time,   xzqh,   ts_title::tsvector as ts_title  ,bd_key ,person ,price::numeric as price
     from cdc.et_gg_%s  
    """%(quyu)
    db_command(sql,dbtype="postgresql",conp=conp_app5)





# quyu="anhui_chuzhou_ggzy"
# conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
# conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']

# update(quyu,conp_gp,conp_app)