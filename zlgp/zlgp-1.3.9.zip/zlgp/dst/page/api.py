from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
import time 
from zlgp.dst.page.core import add_quyu_tmp,restart_quyu_tmp
import traceback

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<阿里云<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def add_quyu_aliyun(quyu):
    conp_hawq=['gpadmin','since2015','192.168.4.183:5433','base_db','page']
    add_quyu_tmp(quyu,conp_hawq)

def restart_quyu_aliyun(quyu):
    conp_hawq=['gpadmin','since2015','192.168.4.183:5433','base_db','page']
    restart_quyu_tmp(quyu,conp_hawq)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>阿里云>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def add_quyu(quyu,loc='aliyun'):
    if loc=='aliyun':
        add_quyu_aliyun(quyu)
    # elif loc=='kunming':
    #     add_quyu_kunming(quyu,tag)

def restart_quyu(quyu,loc='aliyun'):
    if loc=='aliyun':
        restart_quyu_aliyun(quyu)
    # elif loc=='kunming':
    #     add_quyu_kunming(quyu,tag)


#add_quyu_all()