#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 通用包：常量

import importlib
import time
import os
import sys

importlib.reload(sys)

# 测试环境3："http://47.93.82.56:8080"
# 预发环境："http://39.96.8.124:8080"
BASEURL = "http://39.96.8.124:8080"

REPORT_PATH = os.getcwd() + '/report'


REPORT_TITLE = "大平台业务接口自动化测试报告" + time.strftime('%Y%m%d', time.localtime(time.time()))
PRO_REPORT_TITLE = "企业项目流程回归测试"
COMMON_REPORT_TITLE = "普通项目流程回归测试"
TEST_REPORT_TITLE = "大平台业务接口自动化测试报告"

# 测试结果常量


# 测试用例常量
METHOD = 'method'
URL = 'url'
DATA = 'data'
NAME = 'name'
NUMBER = 'number'
CODE = 'code'
HEADERS = 'headers'
VPROJECT_ID = 2927

# 邮件常量
MAIL_HOST = 'smtp2525.sendcloud.net'
MAIL_USER = 'tezign_send'
MAIL_PASS = 'hhIksYtHPnH2l7dj'

MAIL_SENDER = 'dev@send.tezign.co'
MAIL_RECEIVER = ['zhengjingjing@tezign.com']

SUBJECT = '接口自动化测试报告'

# 数据库常量
# DB_HOST = '123.57.137.216'
# DB_USER = 'test'
# DB_PASSWORD = 'tezign'
# DB_NAME = 'tezign_uat'

DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_NAME = 'demo'
DB_SQL1 = "select case_info from t_case where id in (select case_id from t_matching where scenario_id in " \
          "(select id from t_scenario where scenario_name like '%招聘管理%'))"
DB_SQL2 = "select scenario_name from t_scenario where scenario_name like '%招聘管理%'"
