# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""
import yagmail
from functools import wraps
import traceback


class PyEmail(object):
    def __init__(self, source_mail, mail_pass, dest_mail):
        self.source_mail = source_mail
        self.mail_pass = mail_pass
        self.dest_mail = dest_mail

    def send_mail(self, sub, content):
        mail_host = "smtp.exmail.qq.com"  # 设置服务器
        mail_port = 465
        mail_user = self.source_mail  # 用户名
        mail_pass = self.mail_pass  # 口令
        server = yagmail.SMTP(mail_user, mail_pass, mail_host, mail_port)
        server.send(self.dest_mail, sub, content)

    def send_err_mail(self, sub):
        def func_wraps(func):
            @wraps(func)
            def func_process(*args, **kwargs):
                try:
                    func(*args, **kwargs)
                except Exception:
                    exstr = traceback.format_exc()
                    self.send_mail(sub, exstr)

            return func_process

        return func_wraps
