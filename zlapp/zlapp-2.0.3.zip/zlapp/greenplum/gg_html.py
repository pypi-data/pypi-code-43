import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC


#gg_html 更新相对独立
def gg_html_all(conp_src,conp_dst):
    sql="select html_key,page from src.t_gg   "
    datadict={"html_key":BIGINT(),
    "page":TEXT()}
    pg2pg(sql,'gg_html',conp_src,conp_dst,chunksize=10000,datadict=datadict)



def gg_html_pk(conp_dst):
    sql="""
    select constraint_name from information_schema.table_constraints
     where constraint_type='PRIMARY KEY' and table_name='gg_html';
     """
    df=db_query(sql,dbtype="postgresql",conp=conp_dst)
    if df.empty:
        sql="alter table public.gg_html add constraint pk_gg_html_html_key primary key(html_key) "
        db_command(sql,dbtype="postgresql",conp=conp_dst)


def get_max_html_key(conp_dst):
    sql="select max(html_key) from public.gg_html"
    df=db_query(sql,dbtype="postgresql",conp=conp_dst)
    max_html_key=df.iat[0,0]
    return max_html_key



def gg_html_cdc(max_html_key,conp_src,conp_dst):
    conp_dst[4]='cdc'

    print('max_html_key',max_html_key)
    sql="select html_key,page as page from src.t_gg where html_key>%d  "%max_html_key
    print(sql)

   
    datadict={"html_key":BIGINT(),
    "page":TEXT()}
    sql1="truncate table cdc.gg_html_cdc;"
    db_command(sql1,dbtype="postgresql",conp=conp_dst)
    pg2pg(sql,'gg_html_cdc',conp_src,conp_dst,chunksize=10000,datadict=datadict,if_exists='replace')
    print("gg_html_cdc写入完毕")

    sql="insert into public.gg_html select * from cdc.gg_html_cdc as a  where not exists(select 1 from  public.gg_html  as b where a.html_key=b.html_key)"
    db_command(sql,dbtype="postgresql",conp=conp_dst)





def update_gg_html(conp_src,conp_dst):

    sql="select tablename from pg_tables where schemaname='public' "

    df=db_query(sql,dbtype='postgresql',conp=conp_dst)

    if 'gg_html' not in df['tablename'].values:
        print("gg_html表不存在，需要全量导入")
        gg_html_all(conp_src,conp_dst)
        print("全量导入完毕，建立主键")
        gg_html_pk(conp_dst)
    else:
        print("gg_html表已经存在，增量更新")
        max_html_key=get_max_html_key(conp_dst)
        gg_html_cdc(max_html_key,conp_src,conp_dst)

# conp_src=['developer','zhulong!123','192.168.4.183:5433','base_db','public']
# conp_dst=['postgres','since2015','192.168.4.207','biaost','public']

