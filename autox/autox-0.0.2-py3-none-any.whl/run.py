#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 执行包：run regression cases begin with "tezign*.json"

import os
import autox.core.myemail as email
import autox.util.common as common

report = None

if os.path.exists(os.getcwd()+'/log'):

    # 每次执行前清空错误日志
    if os.path.isfile(os.getcwd()+'/log/error.log'):
        f = open(os.getcwd()+'/log/error.log', 'r+')
        f.truncate()
    else:
        pass
else:
    os.mkdir(os.getcwd()+'/log')

if os.path.exists(os.getcwd()+'/report'):
    pass
else:
    os.mkdir(os.getcwd()+'/report')

regTest = common.MyRegression()


def run(scenario_name):
    global report
    report = regTest.build_report(scenario_name)
    # email.email(report)













