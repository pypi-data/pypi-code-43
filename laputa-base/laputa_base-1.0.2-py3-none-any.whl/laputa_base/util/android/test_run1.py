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
2019-05-24          Long Li             add script select func
"""
import multiprocessing
import os
import platform
import time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.config.laputa_config import app_version, url, re_udid, allure_path
from src.config.package.si import get_package
from src.util.android.cmd import Cmd
from src.util.android.server import Server
from src.util.android.write_check import WriteCheck
from src.util.android.get_case import json_to_excel
from src.util.android.get_run_case_id import make_case_path, choose_case
from src.util.android.upload import upload
from src.util.android.operation_json import OperationJson

os.environ['get_log'] = 'true'
os_name = platform.system()
# test_activity_id = os.getenv('BUILD_URL')
package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/package'))
f = get_package(url)

test_type = os.getenv('test_type')


def run_case(i, data, script_path,report_path=None):
    if isinstance(script_path, list):
        script_path = script_path[i % 5]
    # starttime = datetime.datetime.now()
    pinfo = data['portinfo_' + str(i)]
    device_name = pinfo['device_name']
    udid = pinfo['udid']
    platform_version = pinfo['platformVersion']
    now = time.strftime('%Y_%m_%d_%H_%M_%S')
    filename = '_'.join([now, device_name, 'android' + platform_version])
    if test_type != '功能':
        report_path = '../../test_report/android/{0}/{2}/{1}'.format(app_version, filename, f)
    cmd = Cmd()
    cmd.create_log_path(report_path, udid)
    # param = {
    #     'phone_id': udid,
    #     'test_activity_id': test_activity_id,
    #     'phone_start_time': str(starttime)
    # }
    # if test_activity_id is not None:
    #     rj = requests.post(golden_host + '/nioapp/device_result/', data=param)
    # 如果设备需不断重启driver，则不设置环境变量，默认不断重启
    if udid in re_udid:
        command = 'pytest --reruns 1 %s --phoneid %s --alluredir %s' % (script_path, i, report_path)
        os.system(command)
    # 如果设备不需要重启driver，则设置fixture变量为session，只会启动一次driver
    elif os_name == 'Windows':
        os.system(
            'set fixture=session && pytest --reruns 1 %s --phoneid %s --alluredir %s' % (script_path, i, report_path))
    else:
        os.system('export fixture=session && pytest --reruns 1 %s --phoneid %s --alluredir %s' % (
            script_path, i, report_path))
    cmd.kill_port(pinfo['port'])
    time.sleep(5)
    if os_name == 'Linux':
        os.system(r'sudo {1} generate {0} -o {0}/html --clean'.format(report_path, allure_path))
    else:
        os.system(r'allure generate {0} -o {0}/html --clean'.format(report_path))
    """
       获取该手机allure报告路径
       找到该路径所有文件及文件夹
       遍历删除所有文件，只保留html
    """
    allure_xml = os.path.abspath(
        os.path.join(os.path.dirname(__file__), report_path))
    xml_files = os.listdir(allure_xml)
    for xml_file in xml_files:
        xf_path = os.path.join(allure_xml, xml_file)
        if os.path.isfile(xf_path):
            os.unlink(xf_path)
    if os.getenv('BUILD_ID') is not None:
        os.system('pwd')
        os.system('sudo mv {0}/log {0}/html'.format(report_path))
        os.system('cd {0}; sudo zip -r html.zip html'.format(report_path))

    # 如果BUILD_URL不为None，请求接口传递该设备测试结束
    # if test_activity_id is not None:
    #     endtime = datetime.datetime.now()
    #     allure_link = 'http://10.143.16.21/androidReport/android/{0}/{2}/{1}/html/'.format(app_version, filename, f)
    #     log_link = 'http://10.143.16.21/androidReport/android/{0}/{2}/{1}/log/'.format(app_version, filename, f)
    #     param = {
    #         'phone_id': udid,
    #         'test_activity_id': test_activity_id,
    #         'phone_end_time': str(endtime),
    #         'phone_log_link': log_link,
    #         'phone_allure_report_link': allure_link
    #     }
    #     rj = requests.post(golden_host + '/nioapp/device_result/', data=param)
    #     print('phone result end:' + rj.text)


def delete_result_json():
    cur_dir = os.getcwd()
    result_path = os.path.abspath(os.path.join(cur_dir, '../../test_report/result'))
    os.chdir(result_path)
    for file in os.listdir(os.getcwd()):
        if file.endswith('.json'):
            os.remove(file)
    os.chdir(cur_dir)


if __name__ == "__main__":
    begin=time.time()
    delete_result_json()
    write = WriteCheck()
    write.init_portinfo()
    server = Server()
    cmd = Cmd()
    device_list = cmd.get_devices()
    # 如果无BUILD_URL环境变量，不传递此接口
    # if test_activity_id is not None:
    #     start_time = datetime.datetime.now()
    #     param = {
    #         'test_activity_id': test_activity_id,
    #         'app_version': app_version,
    #         'app_build_number': url,
    #         'os_type': 'Android',
    #         'starttime': str(start_time)
    #     }
    #     ret = requests.post(golden_host + '/nioapp/test_activity/', data=param)
    # 多进程启动server
    server_list = list()
    for i in range(len(device_list)):
        s = multiprocessing.Process(target=server.get_appium_command, args=(i,))
        s.start()
        server_list.append(s)
    for s in server_list:
        s.join()
    time.sleep(20)
    data = WriteCheck().director_get_data('portinfo_android.yaml')
    # 多进程运行测试用例
    test_list = list()
    # test_path = write.get_test_model()
    level=os.getenv('level')
    level_choose=os.getenv('level_choose') if os.getenv('level_choose') is not None else 'true'
    module=os.getenv('module')
    module_choose=os.getenv('module_choose') if os.getenv('module_choose') is not None else 'true'
    rp = choose_case(level=level,level_choose=level_choose,module=module,module_choose=module_choose)
    test_path = ' -s '+' '.join(make_case_path(rp))+' '
    if os.getenv('run_phone') != 'true':
        case1 = '-s ../../test_case/android_test/test_SD_SQE_NIOAppInt_install_00100.py '
        test_path = ['-s ../../test_case/android_test/test_surprise ',
                     '-s ../../test_case/android_test/test_mine ',
                     '-s ../../test_case/android_test/test_friends ',
                     '-s ../../test_case/android_test/test_my_car ',
                     '-s ../../test_case/android_test/test_detect ']
        test_path = [i + case1 for i in test_path]
    report_path = '../../test_report/android/%s/%s/%s' % (app_version, f, os.getenv('BUILD_ID')) if test_type=='功能' else ''
    for i in range(len(device_list)):
        # for i in range(1):
        t = multiprocessing.Process(target=run_case, args=(i, data, test_path,report_path))
        t.start()
        test_list.append(t)
    for t in test_list:
        t.join()
    json_to_excel('android_result', 'android')
    if test_type =='功能':
        os.environ['WORKSPACE']=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../'))
        device=device_list[0]
        file = '../../test_report/result/case_result_%s.json' % device
        oj = OperationJson(file=file)
        data=oj.read_json()
        result={'duration':time.time()-begin,'result':data[device],'device':device}
        upload('Android',test_type,app_version,result=result,file=report_path+'/html.zip')
    # 测试活动结束，传递活动结束接口
    # if test_activity_id is not None:
    #     rj = requests.get(url=golden_host + '/nioapp/test_activity/?test_activity_id=%s' % test_activity_id)
    #     print('activity:', rj.text)
