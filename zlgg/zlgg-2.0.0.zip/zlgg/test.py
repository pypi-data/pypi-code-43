from zlgg.core import getpage ,to_arr
from lmf.bigdata import pg2pg
from lmf.dbv2 import db_query 
from zlgg.core.words import initwords_ol, initwords_local
from zlgg.analysis.table import calsep 
from zlgg.clear import  tb_clear,ps_clear
from zlgg.extdata import extall 

from zlgg.stddata import kv
import sys 

krr,krrdict=initwords_ol()

with open(sys.path[0]+'\\test.html','r',encoding='utf8') as f :
    page=f.read()
#tb=tb_clear(page)[0]



data=extall(page,krr)

# df=db_query("select page from v3.t_gg where quyu='anhui_anqing' limit 100",dbtype="postgresql",conp=["gpadmin","since2015","192.168.4.179","base_db","v3"])

# df['minfo']=df['page'].map(lambda x:extall(x,krr))
# df['info']=df['minfo'].map(lambda x:kv(x,krrdict))

def tran_quyu(quyu):
    sql="select * from v3.t_gg where quyu='%s' "%quyu

    conp_hawq=["gpadmin",'since2015','192.168.4.179','base_db','v3']
    conp_pg=['postgres','since2015','192.168.4.188','gg','public']

    pg2pg(sql,'t_gg_%s'%quyu,conp_hawq,conp_pg,chunksize=10000)


