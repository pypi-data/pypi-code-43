#! usr/bin/python
# -*- coding:utf8 -*-
"""
读取文件的脚本

参考日志行：
[pid: 6814|app: 0|req: 1990/15726]
110.90.29.160 () {60 vars in 2074 bytes}
[Mon Sep  9 10:17:57 2019] POST /api/order/order_detail => generated 2558 bytes in 83 msecs
(HTTP/1.1 200) 7 headers in 403 bytes (2 switches on core 1)
"""

import os
import re
import asyncio

import yagmail


class Filereader:
    """读取文件"""
    def __init__(self, filename, logreader, mailsender, wait_time=1.0):
        """初始化日志阅读器，并检验是否为正确的日志文件
        :param filename: string 文件地址
        :param logreader: Logreader object 日志解析类
        :param wait_time: int default=1 跟踪文件变化的间隔时间
        """
        self.filename = filename
        self.logreader = logreader
        self.mailsender = mailsender
        self.wait_time = wait_time
        self.error_log = []

        self._validate_filename()

    async def tail(self):
        """实现tail命令，跟踪文件动态"""
        with open(self.filename) as f:
            f.seek(0, 2)
            i = 0
            while True:
                current_position = f.tell()
                line = f.readline()
                if not line:
                    f.seek(current_position)
                    await asyncio.sleep(self.wait_time)
                else:
                    i += 1
                    await self.read_log(line)

    async def read_log(self, line):
        """读取日志，根据情况进行处理
        :param line: string logline
        """
        result = self.logreader.get_log_info(line)
        # 未匹配到结果，非正常日志信息，记录
        if result is None:
            self.error_log.append(line)
        # 如果出现状态码500，表示错误返回，此时连同之前记录的错误信息，一同通知收件人
        elif result.get('resp_status', '') == '500':
            # 通知收件人
            self.error_log.append(line)
            self._send_email()
            # 清空错误日志记录
            self.error_log = []

    def _send_email(self):
        """发送邮件通知收件人"""
        self.mailsender.send_email(subject='异常日志通知', contents=''.join(self.error_log))

    def _validate_filename(self):
        """确认文件存在、可读、并且不是文件夹"""
        if not os.access(self.filename, os.F_OK):
            raise FileNotFoundError('日志文件 ' + self.filename + ' 不存在')
        if not os.access(self.filename, os.R_OK):
            raise FileNotFoundError('日志文件 ' + self.filename + ' 不可读')
        if os.path.isdir(self.filename):
            raise FileNotFoundError(self.filename + ' 是文件夹而非日志文件')


class Logreader:
    """分析日志"""

    def __init__(self, re_pattern=r''):
        self.pattern = re.compile(re_pattern, re.VERBOSE)

    def get_log_info(self, line):
        """用正则表达式解析log，如果满足表达式，返回解析结果，否则返回None"""
        result = self.pattern.search(line)
        if result:
            return result.groupdict()
        else:
            return result


class Mailsender:
    """邮件处理类"""
    def __init__(self, emailconfig):
        """初始化邮件类
        :param emailconfig: Emailconfig
        """
        self.yagmail = yagmail.SMTP(emailconfig.sender, emailconfig.password,
                                    host=emailconfig.host, port=emailconfig.port)
        self.recipients = emailconfig.recipients

    def send_email(self, subject, contents):
        """发送邮件
        :param subject: string email subject
        :param contents: string message to send
        """
        self.yagmail.send(to=self.recipients, subject=subject, contents=contents)
