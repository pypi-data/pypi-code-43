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
import json
import os

get_path = lambda p: os.path.abspath(os.path.join(os.path.dirname(__file__), '../../test_report/android/result/%s' % p))


class OperationJson:

    def __init__(self, file='case_result.json'):
        self.file = get_path(file)

    def write_json(self, data, file=''):
        file = self.file if file == '' else file
        with open(file, 'w', encoding='utf8') as fp:
            json.dump(data, fp, indent=2)

    def read_json(self, file=''):
        file = self.file if file == '' else file
        if not os.path.exists(file):
            data = dict()
            self.write_json(data, file)
        with open(file) as fp:
            data = json.load(fp)
        return data

    def get_json_result(self, file):
        with open(get_path(file)) as fp:
            return json.load(fp)


if __name__ == '__main__':
    data = {}
    oj = OperationJson()
    d = oj.read_json()
    print(d)
