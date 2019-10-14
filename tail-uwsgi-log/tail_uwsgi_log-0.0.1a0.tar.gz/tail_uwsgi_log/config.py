#! /usr/bin/python
# -*- coding:utf8 -*-

from tail_uwsgi_log.credentials import MAIL_ADDRESS, PASSWORD


class Emailconfig:
    """邮件发送配置类"""
    def __init__(self, recipients, sender='', password='', host='smtp.gmail.com', port=465):
        """
        :param recipients: list 收件人列表
        :param sender: string 发送人
        :param password: string 登录密码
        """
        self.recipients = recipients
        self.sender = MAIL_ADDRESS if sender == '' else sender
        self.password = PASSWORD if password == '' else password
        self.host = host
        self.port = port


class Logconfig:
    """日志文件解析配置类，如文件地址、解析方式、错误通知人等"""
    pattern = r'''\]\ (?P<ip>.*?)\ (.*)\ {.*?}\ \[(?P<datetime>.*?)\]\ (?P<request_method>POST|GET|DELETE|PUT|PATCH)\s
            (?P<request_uri>[^ ]*?)\ =>\ generated\ (?:.*?)\ in\ (?P<resp_msecs>\d+)\ msecs\s
            \(HTTP/[\d.]+\ (?P<resp_status>\d+)\)'''

    def __init__(self, filepath, emailconfig, pattern='', wait_time=1.0):
        self.filepath = filepath
        self.emailconfig = emailconfig
        self.wait_time = wait_time

        if '' != pattern:
            self.pattern = pattern


my_emailconfig = Emailconfig(recipients=['kant@kantli.com'], host='smtp.qq.com')


files = [
    Logconfig(filepath='/users/kant/desktop/uwsgi-t1.log', emailconfig=my_emailconfig, wait_time=0.5),
    Logconfig(filepath='/users/kant/desktop/uwsgi-t2.log', emailconfig=my_emailconfig),
]
