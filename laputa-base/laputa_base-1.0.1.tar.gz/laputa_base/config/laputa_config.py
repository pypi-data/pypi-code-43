# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (C) 2016-2019 Zhiyang Liu in Software Development of NIO/NEXTEV) All rights reserved.
Author: zhiyang.liu.o@nio.com
Date: 2019-05-20

History:
---------------------------------------------
Modified            Author              Content
"""
import os
import re
import sys
import traceback

from laputa_base.config.user_config import *

url = os.getenv('url')
if 'android' in str(traceback.extract_stack()).lower():
    if url is None:
        url = android_url
    url = url.replace('.png', '.apk')
    full_version = re.search('v\d+.\d+.\d+_dev_\d+-\d+', url).group().replace('dev_', '')
    app_version = full_version[1:-15] + full_version[-11:-2]
elif 'ios' in str(traceback.extract_stack()).lower():
    if url is None:
        url = ios_url
    full_version = re.search('lifestyle_\d+.\d+.\d+_\d+-\d+', url).group().replace('lifestyle_', '')
    app_version = full_version[:-15] + full_version[-11:-2]

host = '10.143.16.21'
port = '22'
username = 'nioapp'
password = 'nioapp1234'
mobile_os = 'android' if 'android' in os.path.abspath(sys.argv[0]).lower() else 'ios'
report_server = 'http://10.143.16.21/laputa_report/%s/' % mobile_os
result_server = 'http://10.143.16.21/laputa_result/%s/' % mobile_os
case_url = 'http://10.143.16.21/smoke_test_case/'
jenkins_path = 'http://jenkins.nevint.com/job/DD_nio-app-int-laputa-%s' % mobile_os
report_transfer_url = 'https://kunlun-manager.nioint.com'
report_shown_url = 'https://kunlun.nevint.com/reporter'
# report_transfer_url = 'https://do-kunlun-manager-qa.nioint.com'
# report_shown_url = 'https://kunlun-front-qa.nioint.com/reporter'

module_dict = {
    '基础功能': 'Basic_functions',
    '车辆控制': 'Car_control',
    '购车': 'Buy_car',
    '车商城附件': 'Car_store',
    '充电地图': 'Charging_map',
    '一键加电': 'Power_up',
    '专属桩': 'Charging_pile',
    'SO': 'SO',
    'Debug': 'Debug',
    '我的订单': 'Order',
    '惊喜': 'Surprise',
    'SCR': 'SCR',
    '发现': 'Detect',  # 临时添加
    '朋友': 'Friends',  # 临时添加
    '爱车': 'My_car',  # 临时添加
    '我的': 'Mine',  # 临时添加
}

case_key = ['case_id', 'case_type', 'page', 'module', 'case_name', 'test_precondition',
            'test_steps', 'expected_results', 'priority', 'automation_available_%s' % mobile_os,
            'test_methods_%s' % mobile_os,  'test_results_%s' % mobile_os, 'test_mobiles_%s' % mobile_os]
