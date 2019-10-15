#! /usr/bin/python
# -*- coding:utf8 -*-


class Emailconfig:
    """邮件发送配置类"""
    def __init__(self, recipients, sender='', password='', host='smtp.gmail.com', port=465):
        """
        :param recipients: list 收件人列表
        :param sender: string 发送人
        :param password: string 登录密码
        """
        self.recipients = recipients
        self.sender = sender
        self.password = password
        self.host = host
        self.port = port


class Logconfig:
    """日志文件解析配置类，如文件地址、解析方式、错误通知人等"""
    pattern = r'''\]\ (?P<ip>.*?)\ (.*)\ {.*?}\ \[(?P<datetime>.*?)\]\ (?P<request_method>POST|GET|DELETE|PUT|PATCH)\s
            (?P<request_uri>[^ ]*?)\ =>\ generated\ (?:.*?)\ in\ (?P<resp_msecs>\d+)\ msecs\s
            \(HTTP/[\d.]+\ (?P<resp_status>\d+)\)'''

    def __init__(self, filepath, pattern='', wait_time=1.0):
        self.filepath = filepath
        self.wait_time = wait_time

        if pattern is not None and '' != pattern:
            self.pattern = pattern
