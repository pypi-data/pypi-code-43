#!/usr/bin/env python
# encoding: utf-8
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin MA
#   Email         : xxmawhu@163.com
#   File Name     : main.py
#   Created Time  : 2019-09-19 19:46
#   Last Modified : 2019-10-07 11:08
#   Describe      :
#
# ====================================================
from . import DB
from . import oper
import glob
import time
import sys
from .config import local_config
rmForce = False
if '-f' in sys.argv:
    rmForce = True

def Rm(afile):
    # rm one file for use of pool.map
    # rm_status is the status of oprater 'mv' or 'rm'
    rm_status = ()
    if rmForce:
        rm_status = oper.RmForce(afile)
    else:
        rm_status = oper.MoveToTrash(afile)
    return rm_status


def obtainAllFile():
    files = []
    for i in sys.argv[1:]:
        files += glob.glob(i)
    return files

def test():
    executor = Pool(local_config.getint('core', 'Num_Processor'))
    logs  =  executor.map(Rm, ['LinuxRecycle.egg-info', 'build'])
    executor.close()
    executor.join() 
    DB.insertDB(logs)

def main():
    if rmForce:
        logs = list(map(oper.RmForce, obtainAllFile()))
    else:
        logs = list(map(oper.MoveToTrash, obtainAllFile()))
    DB.insertDB(logs)
if __name__ == "__main__":
    main()
    exit(0)
