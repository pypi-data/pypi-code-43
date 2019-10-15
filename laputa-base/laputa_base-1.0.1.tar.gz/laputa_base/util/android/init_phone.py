# !/usr/bin/env python3
# coding=utf-8
"""
Copyright (C) 2016-2019 Li Long in Software Development of NIO/NEXTEV) All rights reserved.
Author: long.li1.o@nio.com
Date: 2019-09-30

History:
---------------------------------------------
Modified            Author              Content
"""
import os
import threading
import shutil
import sys
import re
import requests

from src.config.laputa_config import url,test_env
from src.pages.elements import app_element
from src.util.android.drivers import Driver
from src.util.android.write_check import WriteCheck
from src.Base.base_android import Base
from src.util.android.cmd import Cmd
from src.business.android.mine_business import MineBusiness
from src.config.account import account

source_path = sys.path[0].replace('\\', '/').split('/src')[0] + '/src/'
package_path = source_path + 'test_report/result/'

def get_package(url):
    pack_name=url.split('/')[-1]
    for file in os.listdir(package_path):
        if pack_name==file:
            return pack_name
    data=requests.get(url,auth=('nio_android', 'NIO_android@190218$'))
    with open(os.path.join(package_path,pack_name),'wb') as fp:
        fp.write(data.content)
    return pack_name

def exec_cmd(phoneid,pack_path):
    os.popen('adb -s %s install -r %s' % (phoneid, pack_path))

def install_package(devices):
    pack_name=get_package(url)
    pack_path=os.path.join(package_path,pack_name)
    for i in range(len(devices)):
        driver = Driver().get_android_driver(i)
        base=Base(i,driver)
        threading.Thread(target=exec_cmd,args=(devices[i],pack_path)).start()
        click_allow_element(base)
        remove_permission_box(i,base)
        driver.quit()


def click_allow_element(base,times=20,click_times=2):
    for i in range(click_times):
        try:
            base.click_loc(app_element.nio_allow_element(base),times=times)
        except:
            break
            
def switch_environment(base):
    ele = base.find_element(app_element.setting_title)
    x, y = ele.location['x'], ele.location['y']
    w, h = ele.size['width'], ele.size['height']
    tx, ty = x + 0.5 * w, y + 0.5 * h
    # print(f'x:{x},y:{y},w:{w},h:{h},tx:{tx},ty:{ty}')
    for i in range(10):
        base.driver.swipe(tx - 10, ty, tx + 10, ty, 100)
    select_server_ele = {
        'name': '切换环境按钮',
        'ele': ('xpath', '//*[@text="Select Server Type"]')
    }
    base.find_element(select_server_ele).click()
    app_element.temp['ele'] = ('xpath', '//*[@text="%s"]' % 'staging' if test_env=='STG' else test_env.lower())
    base.find_element(app_element.temp).click()
    base.driver.press_keycode(4)

def remove_permission_box(i,base):
    base.driver.launch_app()
    click_allow_element(base,times=8)
    base.click_loc(app_element.main_mine)
    base.click_loc(app_element.my_settings)
    text = base.find_element(app_element.setting_version_name).text
    pack_version = re.search('v(\d+.\d+.\d+)', url, flags=re.IGNORECASE).group(1)
    print(text)
    print(pack_version)
    if 'V' + pack_version + '(staging)' != text:
        switch_environment(base)
        base.click_loc(app_element.main_mine)
        base.click_loc(app_element.my_settings)
        text = base.find_element(app_element.setting_version_name).text
        assert 'V' + pack_version + '()' == text
    else:
        base.driver.press_keycode(4)
    MineBusiness(i,base.driver).log_in(account[i]['owner'])
    base.click_loc(app_element.main_friend)
    base.click_loc(app_element.friend_button)
    base.click_loc(app_element.change('cn.com.weilaihui3:id/ll_friend_item_root','id'))
    base.click_loc(app_element.friend_chat)
    base.click_loc(app_element.chat_voice)
    click_allow_element(base,times=5,click_times=1)
    base.click_loc(app_element.chat_add)
    base.click_loc('照片')
    click_allow_element(base, times=5, click_times=1)
    base.driver.press_keycode(4)
    base.click_loc(app_element.chat_add)
    base.click_loc('拍摄')
    click_allow_element(base, times=5, click_times=1)
    base.driver.press_keycode(4)
    base.click_loc(app_element.chat_add)
    base.click_loc('发送位置')
    click_allow_element(base, times=5, click_times=1)
    base.back_to_expect(app_element.main_friend)

if __name__ == '__main__':
    #get_package(url)
    install_package(devices=Cmd().get_devices())