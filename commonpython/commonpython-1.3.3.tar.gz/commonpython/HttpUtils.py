#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@file: HttpUtils.py
@time: 2019/07/09
"""
import requests,traceback
from commonpython.DateUtils import DateUtils


class HttpResponseError(object):
    '''
    error类
    '''
    def __init__(self,error):
        self.error = error
        self.text = 'http response error:{}'.format(self.error)
        self.res_time = 0
        self.headers = 'http header error'
        self.cookies = 'http cookie error'
        self.status_code = 500

    def json(self):
        return 'http response error:{}'.format(self.error)

    def __getattr__(self, item):
        return 'http error {}'.format(item)

class HttpUtils(object):
    '''链式调用'''
    def __init__(self,url):
        self.url = url
        self.session = requests.session()
        self.header = {}
        self.data = {}

    def setData(self,data):
        '''
        设置data
        :param data:  dict
        :return:
        '''
        self.data = data
        return self

    def setHeader(self,header):
        '''
        设置header
        :param data:  dict
        :return:
        '''
        self.header = header
        return self

    def get(self):
        '''
        get方法
        :return:  有参数调用setData
        '''
        res_obj = self.session.get(url=self.url,params=self.data)
        return res_obj

    def post(self):
        '''
        post请求，根据Content-Type判断参数格式
        :return:
        '''
        if 'application/json' in self.header.get('Content-Type',''):
            res_obj = self.session.post(url=self.url,json=self.data,headers=self.header)
        else:
            res_obj = self.session.post(url=self.url, data=self.data, headers=self.header)
        return res_obj

    def start(self,method):
        '''
        调用入口
        :param method:   方法
        :return:  调用对象,响应时间,单位毫秒(ms)
        '''
        if hasattr(self,method):
            start_time = DateUtils().unix_millisecond()
            try:
                res_obj = getattr(self,method)()
            except Exception as e:
                res_obj = HttpResponseError(traceback.format_exc())
            end_time = DateUtils().unix_millisecond()
            run_time = end_time - start_time
            return res_obj,run_time
        else:
            return 'method is not allow',0

if __name__ == '__main__':
    res = HttpUtils("http://xxx:9000/taskapi/TobRiskResult").setData({"testdata":"testdata"}).setHeader({"testhe":"testhe"}).start('get')
    print(res[0].text,res[1])
