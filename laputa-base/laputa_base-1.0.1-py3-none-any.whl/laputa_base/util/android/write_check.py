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
import os
import yaml

current_path = os.path.abspath(os.path.dirname(__file__))
cfg_path = os.path.abspath(current_path + '/../../config')


class WriteCheck:

    def __init__(self, path=cfg_path):
        self.path = path

    def director_get_data(self, filename):
        with open(self.path + '/' + filename, encoding='UTF-8') as fp:
            data = yaml.load(fp, Loader=yaml.FullLoader)
        return data

    def director_get_ele_list(self, filename):
        data = self.director_get_data(filename)
        ele_list = []
        for i in range(1, len(data) + 1):
            value = data['ele' + str(i)]
            ele_list.append([value['ele'], value['name']])
        return ele_list

    def init_portinfo(self):
        from src.util.android import cmd
        cmd = cmd.Cmd()
        device_list = cmd.get_devices()
        with open(self.path + '/portinfo_android.yaml', 'w') as f:
            for i in range(len(device_list)):
                udid = device_list[i]
                data = {
                    'portinfo_' + str(i): {
                        'port': 4700 + i * 2,
                        'bport': 4701 + i * 2,
                        'udid': udid,
                        'platformVersion': cmd.get_system_version(udid),
                        'device_name': cmd.get_phone_name(udid),
                        'systemPort': 8200 + i * 2,
                        'cport': 9517 + i * 2,
                        'brand': cmd.get_phone_product(udid),
                        'size': cmd.get_screen_size(udid),
                        'dimension': cmd.get_physical_dimension(udid)
                    }
                }
                yaml.dump(data, f)


if __name__ == '__main__':
    print(current_path, cfg_path)
    wc = WriteCheck()
    # print(wc.director_get_data('lightenMyPage.yaml'))
