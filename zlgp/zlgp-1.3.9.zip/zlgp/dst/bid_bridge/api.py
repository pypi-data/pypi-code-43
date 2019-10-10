from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 

from  zlgp.dst.bid_bridge.core import add_quyu_tmp,restart_quyu_tmp
import traceback
from zlgp import gp_settings
#昆明云
def add_quyu(quyu,tag='all',loc='aliyun'):
    conp_gp=gp_settings[loc]['conp_gp']
    if quyu in ['anhui_anqing_ggzy','anhui_chaohu_ggzy']:
        add_quyu_tmp(quyu,conp_gp)
    elif quyu.startswith('zlsys'):
        add_quyu_tmp(quyu,conp_gp)
    else:
        print("暂不支持 区域%s"%quyu)


def restart_quyu(quyu,loc='aliyun'):
    conp_gp=gp_settings[loc]['conp_gp']
    if quyu in ['anhui_anqing_ggzy','anhui_chaohu_ggzy']:
        restart_quyu_tmp(quyu,conp_gp)
    elif quyu.startswith('zlsys'):
        restart_quyu_tmp(quyu,conp_gp)
    else:
        print("暂不支持 区域%s"%quyu)



