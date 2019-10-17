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
2019-06-11          Li Long             删除scroll_un方法，与scroll_ele合并
"""
import datetime
import os
import sys
import allure
import time
from PIL import Image
from io import BytesIO
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from laputa_base.config.laputa_config import adb_path
from laputa_base.util.android.write_check import WriteCheck
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.by import By


class Base:
    def __init__(self, i, driver):
        self.i = i
        self.t = 0.5
        data = WriteCheck().director_get_data('portinfo_android.yaml')
        info = data['portinfo_' + str(self.i)]
        self.udid = info['udid']
        self.brand = info['brand']
        self.size = info['size']
        self.driver = driver
        self.ele_list = ''  # 解决循环滑动列表需要重复定位列表问题

    # 获取屏幕截图
    def get_screen(self, name="截图", switch=True):
        print(datetime.datetime.now(), name)
        if switch is False:
            return
        im = Image.open(BytesIO(self.driver.get_screenshot_as_png()))  # Image加载截图bytes数据流
        size = (im.size[0] / 5, im.size[1] / 5)  # 根据截图大小计算压缩后截图分辨率
        im.thumbnail(size)  # 图片压缩
        temp = BytesIO()  # 初始化二进制流
        im.save(temp, 'png')  # 将图片数据写入至二进制数据流
        im_bytes = temp.getvalue()  # 读取二进制流 （将img数据类型转化为bytes数据类型）
        allure.attach(name=name, body=im_bytes, attachment_type=allure.attachment_type.PNG)

    # 检查toast是否出现
    def get_toast_element(self, text: str, times=10, switch=True):
        loc = {'name': "toast弹窗", 'ele': ('xpath', '//*[contains(@text,"%s")]' % text)}
        # loc = {'name': "toast弹窗", 'ele': (By.PARTIAL_LINK_TEXT,text)}
        ele = self.find_element(loc, times=times, switch=switch)
        return ele

    # 定位元素
    def find_element(self, loc, times=8, switch=True):
        if isinstance(loc, str):
            if loc.startswith('//'):
                loc = {'name': loc, 'ele': (By.XPATH, loc)}
            else:
                loc = {'name': loc, 'ele': (By.XPATH, '//*[@text="%s"]' % loc)}
        try:
            ele = WebDriverWait(self.driver, times, self.t).until(ec.presence_of_element_located(loc['ele']))
            self.get_screen('%s定位成功截图' % loc['name'], switch)
            return ele
        except:
            self.get_screen('%s定位失败截图' % (loc['name']), switch)
            raise

    # 定位元素列表
    def find_element_list(self, loc, times=8, switch=True):
        if isinstance(loc, str):
            if loc.startswith('//'):
                loc = {'name': loc, 'ele': (By.XPATH, loc)}
            else:
                loc = {'name': loc, 'ele': (By.XPATH, '//*[@text="%s"]' % loc)}
        try:
            ele = WebDriverWait(self.driver, times, self.t).until(ec.presence_of_all_elements_located(loc['ele']))
            self.get_screen('%s定位成功截图' % loc['name'], switch)
            return ele
        except:
            self.get_screen('%s列表为空' % (loc['name']), switch)
            return []

    # 检查页面元素是否存在
    def check_element_is_exists(self, elements: list, is_scroll=False, director='up', swipe_times=15):
        for ele in elements:
            try:
                if is_scroll:
                    self.swipe_find(ele, director=director, swipe_times=swipe_times, switch=False)
                else:
                    self.find_element(ele, times=10, switch=False)
                allure.attach(ele['name'], '查找成功')
            except:
                self.get_screen(ele['name'] + '定位失败截图', switch=True)
                raise

    # 初始定位一个元素坐标，将期望元素滑动到该坐标
    def swipe_ele_to_expect_location(self, expect_loc, swipe_loc,times=1500):
        expect_ele = self.find_element(expect_loc)
        end_x, end_y = expect_ele.location['x'], expect_ele.location['y']
        swipe_ele = self.swipe_find(swipe_loc)
        start_x, start_y = swipe_ele.location['x'], swipe_ele.location['y']
        os.system(adb_path + ' -s %s shell input swipe %i %i %i %i %i' % (self.udid, start_x, start_y, end_x, end_y,times))

    def click_loc(self, loc, times=8, switch=True):
        ele = self.find_element(loc, times, switch)
        ele.click()

    def send_text(self, loc, text, times=8, switch=True):
        ele = self.find_element(loc, times, switch)
        ele.send_keys(text)

    def get_ele_center(self,ele):
        x, y = ele.location['x'], ele.location['y']  # 控件起点
        w, h = ele.size['width'], ele.size['height']  # 控件大小
        center_x = x + w / 2
        center_y = y + h / 2
        return center_x,center_y

    # 不可点击页面click重新封装
    def click(self, find_loc=None, x=None, y=None):
        if find_loc is not None:
            x, y = find_loc.location['x'], find_loc.location['y']  # 控件起点
            w, h = find_loc.size['width'], find_loc.size['height']  # 控件大小
            center_x = x + w / 2
            center_y = y + h / 2
        elif x is not None and y is not None:
            if x < 1 and y < 1:
                center_x, center_y = self.size['x'] * x, self.size['y'] * y
            else:
                center_x = x
                center_y = y
        else:
            raise Exception
        print(center_x,center_y)
        os.system(adb_path + ' -s %s shell "input tap %i %i"' % (self.udid, center_x, center_y))

    # 不可点击页面click 可点击区域小于控件大小
    def click_temp(self, find_loc, min_x=0.5, min_y=0.5):
        x, y = find_loc.location['x'], find_loc.location['y']  # 控件起点
        w, h = find_loc.size['width'], find_loc.size['height']  # 控件大小
        center_x = x + w * min_x
        center_y = y + h * min_y
        os.system(adb_path + ' -s %s shell "input tap %i %i"' % (self.udid, center_x, center_y))

    # 控件内滑动
    def scroll_ele(self, director='up', size=0.7, scroll_ele='R', scroll_seq=1,
                   find_scroll_time=10, swipe_time=1000, find_switch=True):
        """
        滑动方式全面修改为adb shell swipe ps：经对比adb shell swipe滑动过程最平缓
        director: 滑动方向： up 向上 down 向下 left 向左 right 向右
        scroll_seq : 如果本页存在多个不同位置的相同类型滑动控件，通过此参数选择滑动的控件（计数从1开始）
        size: 滑动比例
        find_switch 循环滑动查找控件是重新定位滑动控件开关
        可滑动元素：ScrollView\RecyclerView\WebView,如有其他元素，直接输入xpath
         1、'android.widget.ScrollView' '爱车'
        'android.support.v7.widget.RecyclerView' '发现4页面滑动元素、我的、搜索'
        'android.webkit.WebView''点亮中国'
        滑动原理：不相关方向选择元素中间坐标值，相关方向两边保留相同宽度
        """
        if find_switch:
            if scroll_ele == 'R':
                recycler_view = {'name': '滑动组件-Recycler',
                                 'ele': ('xpath', '//android.support.v7.widget.RecyclerView[%i]' % scroll_seq)}
                self.ele_list = self.find_element(recycler_view, times=find_scroll_time, switch=False)
            elif scroll_ele == 'S':
                scroll_view = {'name': '滑动组件-Scroll', 'ele': ('xpath', '//android.widget.ScrollView[%i]' % scroll_seq)}
                self.ele_list = self.find_element(scroll_view, times=find_scroll_time, switch=False)
            elif scroll_ele == 'W':
                web_view = {'name': '滑动组件-WebView', 'ele': ('xpath', '//android.webkit.WebView[%i]' % scroll_seq)}
                self.ele_list = self.find_element(web_view, times=find_scroll_time, switch=False)
            elif scroll_ele == 'V':  # 有新的类型时启用
                view = {'name': '滑动组件-View', 'ele': ('xpath', '//android.view.View[%i]' % scroll_seq)}
                self.ele_list = self.find_element(view, times=find_scroll_time, switch=False)
            else:
                if type(scroll_ele) == dict:
                    other_view = scroll_ele
                elif type(scroll_ele) == tuple:
                    other_view = {'name': '滑动组件-自定义', 'ele': scroll_ele}
                elif type(scroll_ele) == str:
                    other_view = {'name': '滑动组件-自定义', 'ele': ('xpath', scroll_ele)}
                self.ele_list = self.find_element(other_view, times=find_scroll_time, switch=False)
        x, y = self.ele_list.location['x'], self.ele_list.location['y']  # 滑动组件起点
        w, h = self.ele_list.size['width'], self.ele_list.size['height']  # 滑动组件大小
        edge_size = (1 - size) / 2  # 边缘留白比例
        if director == 'up':
            orders = adb_path + ' -s %s shell "input swipe %i %i %i %i %i"' \
                     % (self.udid, x + w / 2, y + h * (1 - edge_size), x + w / 2, y + h * edge_size, swipe_time)
            swipe_size = h * size
        elif director == 'down':
            orders = adb_path + ' -s %s shell "input swipe %i %i %i %i %i "' \
                     % (self.udid, x + w / 2, y + h * edge_size, x + w / 2, y + h * (1 - edge_size), swipe_time)
            swipe_size = h * size
        elif director == 'left':
            orders = adb_path + ' -s %s shell "input swipe %i %i %i %i %i"' \
                     % (self.udid, x + w * (1 - edge_size), y + h / 2, x + w * edge_size, y + h / 2, swipe_time)
            swipe_size = w * size
        elif director == 'right':
            orders = adb_path + ' -s %s shell "input swipe %i %i %i %i %i"' \
                     % (self.udid, x + w * edge_size, y + h / 2, x + w * (1 - edge_size), y + h / 2, swipe_time)
            swipe_size = w * size
        else:
            raise Exception('滑动方向设定为"up""down""left""right"，当前为%s,参数错误，请重新确认' % director)
        os.system(orders)
        allure.attach('滑动方向：%s' % director, '滑动距离：%s ' % str(swipe_size))
        return [y, y + h]

    # 滑动查找元素
    def scroll_find(self, loc, director='up', scroll_ele='R', scroll_seq=1, find_time=2, swipe_times=15, size=0.6,
                    swipe_time=700, find_scroll_time=10, switch=True):
        """
        scroll_ele：默认值： R S W V对应滑动组件首字母
        滑动判定元素是否出现在当前页面的方式为：判断元素所在位置
        向上滑动时，避免系统导航栏和app导航栏遮挡
        向下滑动时，避免系统状态栏遮挡
        最终成功或失败前的滑动查找不进行截图，避免过多日志干扰
        """
        height_list = list()  # 获取滑动组建y轴坐标
        windows_height = int(self.size['y'])  # 获取屏幕高度
        for i in range(swipe_times):
            try:
                if isinstance(loc, str) and '//' not in loc:
                    loc = {'name': loc, 'ele': ('xpath', '//*[@text="%s"]' % loc)}
                ele = self.find_element(loc, find_time, switch=False)
                if len(height_list) > 0:  # 滑动一次获取滑动组件坐标后，进入此流程
                    if director == 'up' and ele.location['y'] > height_list[1]:
                        raise Exception('上划时元素起点低于滑动组建最低位置，按未出现处理')
                    elif director == 'down' and (ele.location['y'] + ele.size['height']) < height_list[0]:
                        raise Exception('下划时元素最低点高于滑动组建最高位置，按未出现处理')
                    elif ele.size['height'] < 6:
                        raise Exception('控件高度小于6，按未出现处理')
                    self.get_screen('%s定位成功截图' % loc['name'], switch)
                    return ele
                else:  # 首次查找判断流程
                    if director == 'up' and ele.location['y'] > windows_height * 0.9:
                        raise Exception('上划时元素起点低于屏幕9/10位置，按未出现处理')
                    elif director == 'down' and (ele.location['y'] + ele.size['height']) < windows_height * 0.05:
                        raise Exception('下划时元素最低点高于屏幕1/20位置，按未出现处理')
                    elif ele.size['height'] < 6:
                        raise Exception('控件高度小于5，按未出现处理')
                    self.get_screen('%s定位成功截图' % loc['name'], switch)
                    return ele
            except:
                if i == swipe_times - 1:
                    with open('fail.xml','w',encoding='utf-8') as fp:
                        fp.write(self.driver.page_source)
                    self.get_screen('%s定位失败截图' % (loc['name']), switch)
                    raise
                find_switch = True
                if i > 0:
                    find_switch = False
                height_list = self.scroll_ele(director, size, scroll_ele, scroll_seq,
                                              find_scroll_time, swipe_time, find_switch)

    # 全屏范围内滑动
    def swipe_all(self, director='up', size=0.8, swipe_time=1000):
        """
        滑动最大区域限定为上下左右各留白10%
        :param director: 滑动方向：up，down，left，right
        :param size: 滑动范围 最大值为1，范围限制分辨率的80%
        :param swipe_time: 滑动一次耗时
        :return: None
        """
        if size > 1:
            raise Exception('滑动比例需控制在1以下，当前值为%s,请重新确认滑动比例' % size)
        y = int(self.size['y'])  # 获取屏幕高度
        x = int(self.size['x'])  # 获取屏幕宽度
        if director == 'up' or director == 'down':
            edge_size = (1 - size) / 2 + 0.2  # 边缘留白比例,上下方向必须留出20%的余量，防止滑动起点在可滑动范围之外
        else:
            edge_size = (1 - size) / 2 + 0.1  # 边缘留白比例
        if director == 'up':
            allure.attach("向上滑动", "滑动长度:{}".format(y * 0.8 * size))
            self.driver.swipe(x / 2, y - y * edge_size, x / 2, y * edge_size, swipe_time)
        elif director == 'down':
            allure.attach("向下滑动", "滑动长度:{}".format(y * 0.8 * size))
            self.driver.swipe(x / 2, y * edge_size, x / 2, y - y * edge_size, swipe_time)
        elif director == 'right':
            allure.attach("向右滑动", "滑动长度:{}".format(x * 0.8 * size))
            self.driver.swipe(x * edge_size, y / 2, x - x * edge_size, y / 2, swipe_time)
        elif director == 'left':
            allure.attach("向左滑动", "滑动长度:{}".format(x * 0.8 * size))
            self.driver.swipe(x - x * edge_size, y / 2, x * edge_size, y / 2, swipe_time)
        else:
            raise Exception('滑动方向设定为"up""down""left""right"，当前为%s,参数错误，请重新确认' % director)

    # 全屏范围滑动查找元素
    def swipe_find(self, loc, director='up', find_time=2, swipe_times=15, size=0.8, swipe_time=1000, switch=True, is_list=False):
        if isinstance(loc, str) and loc.startswith('//') is False:
            loc = {'name': loc, 'ele': (By.XPATH, '//*[@text="%s"]' % loc)}
        y = int(self.size['y'])  # 获取屏幕高度
        for i in range(swipe_times):
            try:
                if is_list:
                    eles = self.find_element_list(loc, find_time, switch=False)
                    if len(eles) == 2:
                        return eles
                    else:
                        raise Exception
                ele = self.find_element(loc, find_time, switch=False)
                if director == 'up' and ele.location['y'] > y * 0.9:
                    raise Exception('上划时元素起点低于屏幕9/10位置，按未出现处理')
                elif director == 'down' and (ele.location['y'] + ele.size['height']) < y * 0.05:
                    raise Exception('下划时元素最低点高于屏幕1/20位置，按未出现处理')
                elif ele.size['height'] < 6:
                    raise Exception('控件高度小于5，按未出现处理')
                self.get_screen('%s已找到截图' % loc['name'], switch)
                return ele
            except:
                if i == swipe_times - 1:
                    self.get_screen('%s未找到截图' % loc['name'], switch)
                    raise
                self.swipe_all(director, size, swipe_time)

    # 滑动查找元素列表
    def scroll_finds(self, loc, find_num=1,director='up', scroll_ele='R', scroll_seq=1, find_time=2, swipe_times=15, size=0.5,
                     swipe_time=1000, find_scroll_time=10, switch=True):
        for i in range(swipe_times):
            try:
                ele = self.find_element_list(loc, find_time, switch)
                if len(ele)<find_num:
                    raise Exception
                return ele
            except:
                if i == swipe_times - 1:
                    raise
                find_switch = True
                if i > 0:
                    find_switch = False
                height_list = self.scroll_ele(director, size, scroll_ele, scroll_seq,
                                              find_scroll_time, swipe_time, find_switch)

    # 返回期望页面
    def back_to_expect(self, loc, times=5):
        """
        解决不同页面返回期望界面时的按键次数不确定问题
        同时保证如意外退出,重新打开app
        方式为判断当前app包名是否为蔚来
        """
        k = 0
        for i in range(times):
            try:
                self.find_element(loc, times=5)
                break
            except:
                self.driver.press_keycode(4)
                if 'cn.com.weilaihui3' not in self.driver.current_package:
                    k += 1
                    if k == 3:
                        allure.attach("返回预期页面", "异常进入至非nio app页面")
                        self.driver.launch_app()
                        break

    # 判断元素是否存在
    def is_exist(self, loc, times=5, switch=True):
        try:
            self.find_element(loc, times, switch)
            return True
        except:
            return False

    # 滑动列表判断元素是否存在
    def is_exist_scroll(self, loc, director='up', scroll_ele='R', scroll_seq=1, find_time=2, swipe_times=15, size=0.5,
                        swipe_time=1000, find_scroll_time=10, switch=True):
        try:
            self.scroll_find(loc, director, scroll_ele, scroll_seq, find_time, swipe_times, size, swipe_time,
                             find_scroll_time, switch)
            return True
        except:
            return False

    def long_press_ele(self, loc, duration=1000):
        '''
        长按操作
        :param loc: dict类型为元素定位方式，list类型为x,y坐标
        :param duration: 触摸屏幕时间
        :return:
        '''
        if isinstance(loc, dict):
            ele = self.find_element(loc)
            TouchAction(self.driver).press(el=ele).wait(duration).release().perform()
        if isinstance(loc, list):
            TouchAction(self.driver).press(x=loc[0], y=loc[1]).wait(duration).release().perform()
