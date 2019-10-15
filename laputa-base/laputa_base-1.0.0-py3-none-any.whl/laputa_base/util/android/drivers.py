# !/usr/bin/env python3
# coding=utf-8
"""
Copyright (C) 2016-2019 Zhiyang Liu in Software Development of NIO/NEXTEV) All rights reserved.
Author: zhiyang.liu.o@nio.com
Date: 2019-05-20

History:
---------------------------------------------
Modified            Author              Content
---------------------------------------------
Modified            Author              Content
2019-05-24          Long Li         update clauses:
                                            add driver time out limit
"""
import time
import os
import traceback

from appium import webdriver

from src.util.android.write_check import WriteCheck
from src.util.android.cmd import Cmd
from src.config.laputa_config import adb_path


class Driver:

    def get_android_driver(self, i):
        write_check = WriteCheck()
        data = write_check.director_get_data('portinfo_android.yaml')
        pinfo = data['portinfo_' + str(i)]
        udid = pinfo['udid']
        port = pinfo['port']
        device_name = pinfo['device_name']
        platformVersion = pinfo['platformVersion']
        systemPort = int(pinfo['systemPort'])
        desired_caps = dict()
        desired_caps['platformName'] = 'Android'
        desired_caps['platformVersion'] = platformVersion
        desired_caps['automationName'] = 'UIAutomator2'
        desired_caps['deviceName'] = device_name
        desired_caps['udid'] = udid
        # desired_caps['autoGrantPermissions'] = True
        # desired_caps['app'] = ''
        desired_caps['appPackage'] = 'cn.com.weilaihui3'
        desired_caps['appActivity'] = 'cn.com.weilaihui3.ui.activity.SplashActivity'
        # desired_caps['appActivity'] = 'cn.com.weilaihui3.app.ui.activity.HomeActivity'
        # desired_caps['autoAcceptAlerts']= True
        desired_caps['noReset'] = True
        desired_caps['systemPort'] = systemPort
        desired_caps['newCommandTimeout'] = 4000
        #desired_caps['chromeOptions'] = {"androidProcess": "cn.com.weilaihui3:tools"}
        # from src.util.android.server import Server
        # server = Server()
        # server.get_appium_command(i)
        # desired_caps['newCommandTimeout'] = 180
        packageList = Cmd().get_cmd_return(adb_path + ' -s %s shell "pm list package -3|grep appium"' % udid)
        for package in packageList:
            if 'appium' in package:
                os.system(adb_path + ' -s %s shell pm clear %s' % (udid, package.split(':')[-1].strip('\n')))
        # Server().get_appium_command(i)
        return webdriver.Remote('http://127.0.0.1:%s/wd/hub' % port, desired_caps)


if __name__ == '__main__':
    dirver=Driver().get_android_driver(0)
    os.system('adb shell uiautomator dump /sdcard/ui.xml')
    input('........')