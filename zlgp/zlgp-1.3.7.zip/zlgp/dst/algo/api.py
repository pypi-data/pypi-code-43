from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
import time 
from zlgp.dst.algo.core import add_quyu_tmp,restart_quyu_tmp #zlgp.dst.algo.
import traceback

from zlgp import gp_settings

def add_quyu(quyu,tag='all',loc='aliyun'):
    conp_gp=gp_settings[loc]['conp_gp']
    add_quyu_tmp(quyu,conp_gp)

def restart_quyu(quyu,loc='aliyun'):
    conp_gp=gp_settings[loc]['conp_gp']
    restart_quyu_tmp(quyu,conp_gp)





