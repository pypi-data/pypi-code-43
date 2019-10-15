# !/usr/bin/env python3
# coding=utf-8
"""
Copyright (C) 2016-2019 Zhiyang Liu in Software Development of NIO/NEXTEV) All rights reserved.
Author: zhiyang.liu.o@nio.com
Date: 2019-05-20

History:
---------------------------------------------
Modified            Author              Content
"""

import threading
import os
import time
from src.config.laputa_config import appium_path
from src.util.android.cmd import Cmd
from src.util.android.write_check import WriteCheck

log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../test_report/appium_log'))
if os.path.exists(log_path) is False:
    os.makedirs(log_path)


class Server:

    def __init__(self):
        self.Cmd = Cmd()
        self.deviceList = self.Cmd.get_devices()
        self.write = WriteCheck()

    def get_appium_command(self, i):
        now = time.strftime('%Y_%m_%d_%H_%M_%S_')
        data = self.write.director_get_data('portinfo_android.yaml')
        pinfo = data['portinfo_' + str(i)]
        port = pinfo['port']
        bport = pinfo['bport']
        udid = pinfo['udid']
        log_file = os.path.join(log_path, now + self.Cmd.get_phone_name(udid) + '_server.log')
        cport = pinfo['cport']
        # rj = requests.get(url=golden_host + '/nioapp/get_device/', params={"phone_id": self.deviceList[i]})
        # if rj.text == '0':
        #     param = {
        #         'phone_id': udid,
        #         'phone_brand': pinfo['brand'],
        #         'phone_type': pinfo['device_name'],
        #         'phone_os_version': 'Android' + pinfo['platformVersion'],
        #         'phone_resolution': '%s*%s' % (pinfo['size']['x'], pinfo['size']['y']),
        #         'phone_size': pinfo['dimension']
        #     }
        #     ret = requests.post(url=golden_host + '/nioapp/device_info/', data=param)
        self.Cmd.kill_port(port)
        if os.name == 'nt':
            appium_cmd = 'start /min "appium" appium -a 127.0.0.1 -p {} -bp {} -U {} --log {} --chromedriver-port {} ' \
                         '--no-reset --session-override'.format(port, bport, udid, log_file, cport)
            os.system(appium_cmd)
        else:
            appium_cmd = appium_path + ' -p {} -bp {} -U {} ' \
                                       '--chromedriver-port {} --session-override'.format(port, bport, udid, cport)
            commod = 'nohup %s > %s &' % (appium_cmd, log_file)
            os.system(commod)

    def main(self):
        tlist = []
        print('devicelist')
        for i in range(len(self.deviceList)):
            t = threading.Thread(target=self.get_appium_command, args=(i,))
            t.start()
            tlist.append(t)
        for t in tlist:
            t.join()


if __name__ == '__main__':
    server = Server()
    server.write.init_portinfo()
    server.main()
