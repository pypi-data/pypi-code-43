#!/usr/bin/env python
# encoding: utf-8
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin MA
#   Email         : xxmawhu@163.com
#   File Name     : config.py
#   Created Time  : 2019-09-19 23:52
#   Last Modified : 2019-09-26 16:00
#   Describe      :
#
# ====================================================
import os
from configparser import ConfigParser
local_config = ConfigParser()
if os.path.exists(os.path.expanduser('~/.mtdb/mtrc')):
    local_config.read(os.path.expanduser('~/.mtdb/mtrc'))
else:
    mtdbDir = os.path.expanduser('~/.mtdb')
    if not os.path.exists(mtdbDir):
        os.mkdir(mtdbDir)
    local_config.add_section('core')
    local_config.set('core', 'Num_Processor', "100")
    local_config.set('core', 'Keep_data_base', "1")
    local_config.set('core', 'keep_days', "30")
    local_config.set('core', 'data_base_file', 
            os.path.expanduser("~/.mtdb/fileInfo.db"))
    local_config.set('core', 'white_files', 
            os.path.expanduser("~/.mtdb/fileInfo.db")+',')
    with open(os.path.expanduser('~/.mtdb/mtrc'), 'w') as configFile:
        local_config.write(configFile)

user = os.environ["USER"]
if __name__ == "__main__":
    print(local_config['core']['Num_Processor'])
    print(local_config['core']['keep_days'])
    print(local_config['core']['data_base_file'])
# print local_config.get('core', 'white_file')
