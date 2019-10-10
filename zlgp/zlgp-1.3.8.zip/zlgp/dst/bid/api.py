from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 

from zlgp.dst.bid.core import add_quyu_tmp_pc,restart_quyu_tmp_pc,add_quyu_zlsys,restart_quyu_zlsys #zlhawq.dst.bid.
import traceback
from zlgp import gp_settings
#昆明云

def add_quyu(quyu,tag='all',loc='aliyun'):
    conp_gp=gp_settings[loc]['conp_gp']
    conp_pg_zlmine=gp_settings[loc]['conp_pg_zlmine']

    if quyu in ['anhui_anqing_ggzy','anhui_chaohu_ggzy']:
        add_quyu_tmp_pc(quyu,conp_gp,conp_pg_zlmine,tag)
    elif quyu.startswith('zlsys'):
        add_quyu_zlsys(quyu,conp_gp)
    else:
        print("暂不支持 区域%s"%quyu)


def restart_quyu(quyu,loc='aliyun'):
    conp_gp=gp_settings[loc]['conp_gp']
    conp_pg_zlmine=gp_settings[loc]['conp_pg_zlmine']

    if quyu in ['anhui_anqing_ggzy','anhui_chaohu_ggzy']:
        restart_quyu_tmp_pc(quyu,conp_gp,conp_pg_zlmine)
    elif quyu.startswith('zlsys'):
        restart_quyu_zlsys(quyu,conp_gp)
    else:
        print("暂不支持 区域%s"%quyu)





