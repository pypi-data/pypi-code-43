#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR: XYCoder
# FILE: ~/Desktop//xyscript/xyscript/test/test.py
# DATE: 2019/08/21 Wed
# TIME: 14:12:21

# DESCRIPTION:


# -*- coding: GB2312 -*-
import os,sys,json,wx
import os.path
import time
from threading import Timer
from threading import Thread
import glob
from xyscript.common.sysenv import System
from xyscript.common.xylog import *
from concurrent.futures import ThreadPoolExecutor, as_completed
from xyscript.common.interaction import Interaction
from xyscript.common.file import File
# from xyscript.test.testUI.te import TestThread

# 获取连接设备
DEVICES = ['xytest']
# 种子数
SEED_NUM = 23
# 延时
TIME_DELAY = 300
# 执行次数
RUN_TIMES = 500000
# 执行方式 --ignore-crashes --ignore-timeouts --ignore-security-exceptions --ignore-native-crashes 
IMPLEMENT_WAY = ['ignore-crashes','ignore-timeouts','ignore-security-exceptions','ignore-native-crashes']
# 日志级别
LOG_LEVEL = ' -v -v -v'
# 日志地址
LOG_ADDRESS = None
# 执行周期
LIFECYCLE = 4
# 执行次数
CYCLES = 3
# 所有在测试的包名
PACKAGES_TESTING = []
# 生成配置文件名称
CONFIG_NAME = 'config.json'
# 当前执行的次数
CURRENT_INDEX = 1
# 线程数
THREAD_NUM = 0



platform = System().get_platform()

class Test:
    def start_test(self):
        ui = TestUI()
        try:
            ui.get_seed_num()
            ui.get_run_times()
            ui.get_run_cycle()
            ui.get_link_mobile()
            self.setup_task_files(ui)
            self.run_monkey_with_config(ui)
        except BaseException as error:
            faillog(format(error))
            # 停掉所有测试进程
            mobile = ui.get_config_with_name('mobile')
            for key,value in mobile.items():
                dev = key.split('_')[-1]
                self.kill_monkey_with_package_name(dev)
                self.kill_logcat(dev)
            sys.exit()

    def stop_test(self,ui,t=None,t0=None):
        mobile = ui.get_config_with_name('mobile')
        for key,value in mobile.items():
            dev = key.split('_')[-1]
            self.kill_monkey_with_package_name(dev)
            self.kill_logcat(dev)
            if t is not None:
                t.join()
            if t0 is not None:
                t0.stop_thread()
            

    def setup_task_files(self,ui):
        data = ui.get_config_with_name()
        mobile_dict = data.get('mobile')
        workspace = data.get('workspace')
        for key,value in mobile_dict.items():
            mobile_folder_path = workspace + key + '/'
            if platform in ["Windows/Cygwin","Windows"]:
                mobile_folder_path = mobile_folder_path.replace('/','\\')
            mobile_folder_path = mobile_folder_path.replace(' ','-')
            if not os.path.exists(mobile_folder_path):
                File().creat_folder(mobile_folder_path)
            # for package_name in value:
            #     package_path = mobile_folder_path + package_name + '/'
            #     if not os.path.exists(package_path):

            #         File().creat_folder(package_path)
        
        logcat_path = workspace + 'logcat/'
        if platform in ["Windows/Cygwin","Windows"]:
            logcat_path = logcat_path.replace('/','\\')
        if not os.path.exists(logcat_path):
            File().creat_folder(logcat_path)
            ui.set_config_with_name('logcat_path',logcat_path)

        
    def run_monkey_with_config(self,ui):
        global CURRENT_INDEX
        timer_interval = 3
        # start_time = time.time()
        executor = ThreadPoolExecutor(max_workers=100)

        mobile_dict = ui.get_config_with_name('mobile')
        array = []
        for key,value in mobile_dict.items():
            array.append(key)
        # 循环次数
        cycles = ui.get_config_with_name('cycles')

        all_task = [executor.submit(self.run_adb_str,(ui),(key)) for (index,key) in enumerate(array)]

        # t = Timer(timer_interval,change_process,[time.time() - start_time,CURRENT_INDEX])
        # t.start()
        over_num = 0
        for index,future in enumerate(as_completed(all_task)):
            # sys.stdout.write("\r进度:%d / %d" %(index+1, len(all_task)))
            # sys.stdout.flush()
            data = future.result()
            if data is None:
                over_num = over_num + 1
                if over_num == len(array):
                    # t.cancel()
                    CURRENT_INDEX = CURRENT_INDEX + 1
                    if CURRENT_INDEX <= cycles:
                        self.run_monkey_with_config(ui)  
        

    def run_adb_str(self,ui,key):
        global CURRENT_INDEX
        # 序列号
        dev = key.split('_')[-1]
        # logcat
        logcat_file_name = key + str(CURRENT_INDEX) + '.log'
        logcat_file_path = ui.get_config_with_name('logcat_path')
        os.popen('adb -s ' + dev + ' shell logcat -c') #清楚日志
        os.popen('adb -s ' + dev + ' shell  logcat -v time > ' + logcat_file_path + logcat_file_name) #记录日志
        # 包名
        packages = ui.get_config_with_name('mobile').get(key)
        p_array = ''
        for p in packages:
            p_array = p_array + ' -p ' + p
        # 种子数
        seed_num = ui.get_config_with_name('seed_num')
        # 模式
        implement_way = ui.get_config_with_name('implement_way')
        run_mode = ''
        for behav in implement_way:
            run_mode = run_mode + ' --' + behav
        # 延迟
        time_delay = ui.get_config_with_name('time_delay')
        # 日志等级
        log_level = ui.get_config_with_name('log_level')
        # 执行次数
        run_times = ui.get_config_with_name('run_times')
        # 日志地址
        workspace = ui.get_config_with_name('workspace')
        log_path = workspace + key + '/'  + key + '_' +str(CURRENT_INDEX) + '.log'
        if  platform in ["Windows/Cygwin","Windows"]:
            log_path = log_path.replace('/','\\')
        log_path = log_path.replace(' ','-')
        
        shell_str = 'adb -s '+ dev +' shell monkey ' + p_array + ' -s ' + str(seed_num) + run_mode + ' --throttle ' + str(time_delay) + ' --pct-touch 40 --pct-motion 25 --pct-appswitch 15 --pct-trackball 5 --pct-majornav 5 ' + log_level + ' ' + str(run_times) + ' >' + log_path + ' 2>&1'
        result =os.popen(shell_str)

        # 每次执行周期
        cycle = ui.get_config_with_name('life_cycle')
        run_time_delay = cycle * 60 * 60
        time.sleep(int(run_time_delay))
        self.kill_monkey_with_package_name(dev)
        self.kill_logcat(dev)

    def kill_logcat(self,dev):
        result = None
        if  platform in ["Windows/Cygwin","Windows"]:
            result= os.popen('adb -s ' + dev + ' shell ps | findstr "logcat"').readlines()
        elif platform in ["Mac OS X","OS/2","OS/2 EMX","Linux"]:
            result= os.popen('adb -s ' + dev + ' shell ps | grep logcat').readlines()

        for line in result:
            pid_str_array = line.split(' ')
            if len(pid_str_array) >= 6:
                pid = pid_str_array[5]
                os.popen('adb -s ' + dev + ' shell kill -9 ' + str(pid)).readlines()

        
    def kill_monkey_with_package_name(self,dev,packages=None):
        adb_result = None
        if  platform in ["Windows/Cygwin","Windows"]:
            adb_result= os.popen('adb -s ' + dev + ' shell ps | findstr "monkey"').readlines()
        elif platform in ["Mac OS X","OS/2","OS/2 EMX","Linux"]:
            adb_result= os.popen('adb -s ' + dev + ' shell ps | grep monkey').readlines()

        for line in adb_result:
            pid_str_array = line.split(' ')
            if len(pid_str_array) >= 6:
                pid = pid_str_array[5]
                os.popen('adb -s ' + dev + ' shell kill ' + str(pid)).readlines()
            

    def get_device_name_with_IMEI(self,IMEI,type):
        result = ''
        # if  platform in ["Windows/Cygwin","Windows"]:
            # adb -s 37KNW18802008494 shell getprop ro.product.brand
        # print('adb -s ' + IMEI + ' shell getprop ro.product.' + type)
        result = os.popen(
            'adb -s ' + IMEI + ' shell getprop ro.product.' + type).readlines() 
        # elif platform in ["Mac OS X","OS/2","OS/2 EMX","Linux"]:
        #     result = os.popen(
        #     "adb -s " + IMEI + ' shell cat /system/build.prop | grep ro.product.' + type +'= ').readlines() 

        if result is not None and len(result)>=1 and len(result[0])>2:
            # print(result[0][:-1])
            return result[0][:-1]
        return None

    def get_package_name_contain(self,IMEI,name=None):
        shell = "adb -s " + IMEI + ' shell pm list packages'
        if name is not None:
            shell = "adb -s " + IMEI + ' shell pm list packages | grep ' + name
            if  platform in ["Windows/Cygwin","Windows"]:
                shell = "adb -s " + IMEI + ' shell pm list packages | findstr ' + name
        
        packages = []
        result = os.popen(shell).readlines()
        for package in result:
            package_str_array = package.split(':')
            if len(package_str_array) >=2:
                packages.append(package.split(':')[1].rstrip())
        return packages

    # def 

class TestUI:
    def __init__(self):
        global SEED_NUM ,TIME_DELAY ,RUN_TIMES ,IMPLEMENT_WAY ,LOG_LEVEL ,LOG_ADDRESS ,LIFECYCLE ,PACKAGES_TESTING ,CONFIG_NAME ,CYCLES
        LOG_ADDRESS = self.get_desktop_path()
        #print(LOG_ADDRESS)
        self.workspace = LOG_ADDRESS
        self.seed_num = SEED_NUM
        self.time_delay = TIME_DELAY
        self.run_times = RUN_TIMES
        self.implement_way = IMPLEMENT_WAY
        self.log_level = LOG_LEVEL
        self.life_cycle = LIFECYCLE
        self.packages_testing = PACKAGES_TESTING
        self.config_name = CONFIG_NAME
        self.cycles = CYCLES
        self.setup_config_file()
# log_store_local = /dist/
# cache_path = /XYCache/
    
    def get_desktop_path(self):
        desktop_path = ''
        cache_path = ''
        sym_path = "monkeytest/"
        if  platform in ["Windows/Cygwin","Windows"]:
            desktop_path = os.path.join(os.path.expanduser("~"), 'Desktop')
            cache_path = desktop_path + '/XYCache/' + sym_path
            cache_path = cache_path.replace('/','\\')
        elif platform in ["Mac OS X","OS/2","OS/2 EMX","Linux"]:
            desktop_path = os.path.expanduser('~')
            cache_path = desktop_path + '/XYCache/' + sym_path

        File().creat_folder(cache_path)
        return cache_path

    def get_workspace(self):
        return Interaction().select_directory(2)


    def get_run_cycle(self):
        default_cycle = self.get_config_with_name('life_cycle')
        cycle = input('请输入每次执行的周期(小时),默认值是 ' + str(default_cycle) + ' 小时:')
        if len(cycle) != 0:
            self.set_config_with_name('life_cycle',float(cycle))

    
    def get_run_times(self):
        default_cycle = self.get_config_with_name('cycles')
        cycles = input('请输入任务循环次数,默认值是 ' + str(default_cycle) + ' 次:')
        if len(cycles) != 0:
            self.set_config_with_name('cycles',int(cycles))

    def get_seed_num(self):
        seed_num = self.get_config_with_name('seed_num')
        seed = input('请输入任务种子数,默认值是 ' + str(seed_num) + ':')
        if len(seed) != 0:
            self.set_config_with_name('seed_num',int(seed))       

    def get_link_mobile(self):
        rt = os.popen('adb devices').readlines()  
        n = len(rt) - 2
        # if UI is not None:
        print ("当前已连接待测手机数为：" + str(n))

        aw = input("是否要继续你的monkey测试，请输入(yes or no): ")

        if aw == 'yes':
            mobile_data = {}
            ds = list(range(n))
            for i in range(n):
                nPos = rt[i + 1].index("\t")
                ds[i] = rt[i + 1][:nPos]
                dev = ds[i]
                # 获取手机型号
                model = Test().get_device_name_with_IMEI(dev,'model')
                # 获取手机名称
                name = Test().get_device_name_with_IMEI(dev,'brand')
                # 包关键字
                package_keyword = input('请输入 ' + model + ' 中需要测试包名关键词:')
                if len(package_keyword) <=0 :
                    package_keyword = None
                # 所有包名
                pk = Test().get_package_name_contain(dev,package_keyword)
                # 需要测试的包名序号
                answer_package_str = '请输入 ' + model + ' 中需要测试包名序号(多个序号按照\',\'分隔):\n'
                for index,package in enumerate(pk):
                    answer_package_str = answer_package_str + str(index + 1) + '.' + package + '\n'
                answer_package_result = input(answer_package_str)
                need_test_package_arr = answer_package_result.split(',')
                mobile_folder_name = name + '_' + model + '_' + dev

                p_array = []
                for index in need_test_package_arr:
                    p_array.append(pk[int(index) -1])

                mobile_data[mobile_folder_name] = p_array

            self.set_config_with_name('mobile',mobile_data)


        elif aw == 'no':
            #print('请重新确认所有待测手机是否已通过adb命令连接至pc!')
            sys.exit()
        else:
            print ("测试结束，输入非法，请重新输入yes or no！")
            sys.exit()

    def get_link_mobile_with_keyword(self,keyword):
        rt = os.popen('adb devices').readlines()  
        n = len(rt) - 2
        mobile_data = {}
        ds = list(range(n))
        for i in range(n):
            if 'offline' in rt[i + 1]:
                break
            nPos = rt[i + 1].index("\t")
            ds[i] = rt[i + 1][:nPos]
            dev = ds[i]
            # # 获取手机型号
            model = Test().get_device_name_with_IMEI(dev,'model')
            # 获取手机名称
            name = Test().get_device_name_with_IMEI(dev,'brand')
            # 包关键字
            package_keyword = keyword
            if len(package_keyword) <=0 :
                package_keyword = None
            # 所有包名
            pk = Test().get_package_name_contain(dev,package_keyword)
            if model is None or name is None:
                break
            mobile_folder_name = name + '_' + model + '_' + dev
            mobile_data[mobile_folder_name] = pk

        self.set_config_with_name('mobile',mobile_data)

    def get_all_devices(self,keyword):
        self.get_link_mobile_with_keyword(keyword)
        mobile = self.get_config_with_name('mobile')
        return mobile

    def get_config_with_name(self,name=None):
        if self.workspace is None:
            self.setup_config_file()
        config_file = self.workspace + self.config_name
        with open(config_file,'r') as f:
            data = json.load(f)
            if name is None:
                return data
            return data.get(name)

    def set_config_with_name(self,name,value):

        config_file = self.workspace  + self.config_name
        if config_file is None:
            self.setup_config_file()
        f = open(config_file,'r')
        data = json.load(f)
        f.close()
        with open(config_file,'w') as fw:
            data[name] = value
            json.dump(data,fw)

    def setup_config_file(self):
        if self.workspace is None:
            self.workspace =  self.get_workspace()

        config_path = self.workspace + '/' + self.config_name
        if  platform in ["Windows/Cygwin","Windows"]:
            config_path = config_path.replace('/','\\')
        if not os.path.exists(config_path):
            with open(config_path, 'w') as fw:
                config = {}
                config['workspace'] = self.workspace
                config['seed_num'] = self.seed_num
                config['time_delay'] = self.time_delay
                config['run_times'] = self.run_times
                config['implement_way'] = self.implement_way
                config['log_level'] = self.log_level
                config['life_cycle'] = self.life_cycle
                config['packages_testing'] = self.packages_testing
                config['cycles'] = self.cycles
                config['device'] = []
                json.dump(config,fw)


class FileManager:
    def start_logcat(self):
        pass



if __name__ == '__main__':

    # Test().start_test()
    TestUI().get_link_mobile_with_keyword('model')

    # dev = ['d934619c','46f1f44e']
    # for de in dev:
    #     adb_result = os.popen('adb -s ' + de + ' shell ps | grep monkey').readlines()
    #     #print(adb_result)
    #     for line in adb_result:
    #         pid = line.split(' ')[5]
    #         result =  os.popen('adb -s ' + de + ' shell kill ' + str(pid))
    #         #print(result)

    # IMEI = 'd934619c'
    # type = 'model'
    # name = ''
    # test = 'adb -s ' + IMEI + ' shell "cat /system/build.prop | grep "ro.product.' + type +'="" '
    # test = "adb -s " + IMEI + ' shell pm list packages | findstr ' + name
    # result = os.popen(test).readlines()
    #print(test)
    #print(result)

    