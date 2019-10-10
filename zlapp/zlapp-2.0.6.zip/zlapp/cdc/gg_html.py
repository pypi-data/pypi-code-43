import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time 

def est_gg_html_quyu(quyu,conp_gp):
  
    sql="""
    CREATE  unlogged  TABLE if not exists etl.gg_html_%s (
    html_key bigint,
    page text
    )
    distributed by(html_key)
    """%(quyu)
    db_command(sql,dbtype='postgresql',conp=conp_gp)




def get_max_html_key(quyu,conp_gp):
    max_html_key=db_query("select max_gg_meta from etlmeta.t_html_key where quyu='%s'"%quyu,dbtype="postgresql",conp=conp_gp).iat[0,0]

    return max_html_key

def pre_quyu_cdc(quyu,conp_gp):
    max_html_key=get_max_html_key(quyu,conp_gp)
    est_gg_html_quyu(quyu,conp_gp)
    sql="truncate table etl.gg_html_%s;"%quyu
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)

    sql1="insert into etl.gg_html_%s select html_key,page from src.t_gg where quyu='%s' and html_key>%d "%(quyu,quyu,max_html_key)
    print(sql1)
    db_command(sql1,dbtype="postgresql",conp=conp_gp)

    df=db_query("select max(html_key),count(*) from etl.gg_html_%s "%quyu,dbtype="postgresql",conp=conp_gp)
    cnt=df.iat[0,1]
    print("此次更新数据 %d 条"%cnt)







def insert_into(quyu,conp_gp,conp_app1):
    user,passwd,host,db,schema=conp_gp
    arr=host.split(":")
    host=arr[0]
    port=arr[1] if len(arr)==2 else '5432'
    sql="""
    with a as (
    select * from dblink('hostaddr=192.168.4.183 port=5433 dbname=base_db user=gpadmin password=since2015',
            $lmf$
            select html_key,page from etl.gg_html_anhui_anqing_ggzy 
          $lmf$) AS testTable ( html_key bigint,page text))
    insert into public.gg_html 

    select * from a   where not exists(select html_key from  gg_html as b where a.html_key=b.html_key)
    """
    sql=sql.replace('192.168.4.183',host)
    sql=sql.replace('5433',port)
    sql=sql.replace('user=gpadmin',"user=%s"%user)
    sql=sql.replace('password=since2015',"password=%s"%passwd)
    sql=sql.replace('anhui_anqing_ggzy',quyu)
    db_command(sql,dbtype="postgresql",conp=conp_app1)


