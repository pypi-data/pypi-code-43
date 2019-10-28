"""
@Time:2019/9/4 16:18
@Author:jun.huang
"""
import smtplib
import time
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import cx_Oracle
import os
import socket
import requests
import pymysql
import pandas as pd

# 数据库相关
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


def dict_key_upper(d):
    n_dict = {}
    for k, v in d.items():
        n_dict[k.upper()] = v
    return n_dict


def dict_key_lower(d):
    n_dict = {}
    for k, v in d.items():
        n_dict[k.lower()] = v
    return n_dict


def timestamp_to_datetime(timestamp, fmt='%Y-%m-%d %H:%M:%S'):

    return time.strftime(fmt, time.localtime(timestamp))


def string_to_datetime(string, fmt='%Y-%m-%d %H:%M:%S'):

    return datetime.datetime.strptime(string, fmt)


def datetime_to_string(dt, fmt='%Y-%m-%d %H:%M:%S'):

    return dt.strftime(fmt)


def datetime_cal(dt, seconds):
    
    return dt + datetime.timedelta(seconds=seconds)


class OracleDataBase:
    def __init__(self, **kwargs):
        """
        :param kwargs:
        connect_flag ：连接是否成功的标识
        host，usrname，password，name 连接数据库的必备配置信息
        db: 数据库连接
        cursor: 游标，用来执行sql
        :return:
        """
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.host = kwargs['host']
        try:
            self.db = cx_Oracle.connect(self.username, self.password, self.host)
            self.cursor = self.db.cursor()
            self.connect_flag = True

        except Exception as e:

            raise Exception("connect to {} failed, the reason:{}".format(self.host, e))

    def execute_dms(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            raise Exception("execute {} failed. the reason {}".format(sql, e))

    def pd_read_sql(self, sql, params=""):
        try:
            data = pd.read_sql(sql, con=self.db, params=params).to_dict('records')
        except Exception as e:
            raise Exception("pd execute {} failed. the reason {}".format(sql, e))
        return data

    def close_db(self):
        self.db.commit()
        self.cursor.close()
        self.db.close()


# 连接mysql的函数
class MysqlDataBase:

    def __init__(self, **kwargs):
        """
        :param kwargs:
        connect_flag ：连接是否成功的标识
        host，usrname，password，name 连接数据库的必备配置信息
        db: 数据库连接
        cursor: 游标，用来执行sql

        :return:
        """
        self.host = kwargs['host']
        self.username = kwargs['user']
        self.password = kwargs['password']
        self.db = kwargs['db']
        self.port = kwargs['port']
        try:
            self.db = pymysql.connect(host=self.host, user=self.username,
                                      password=self.password, db=self.db, port=self.port,
                                      charset='utf8')
            self.cursor = self.db.cursor()
        except Exception as e:

            raise Exception("connect to {} failed, the reason:{}".format(self.host, e))

    def execute_dms(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            raise Exception("execute {} failed. the reason {}".format(sql, e))

    def pd_read_sql(self, sql, params=""):
        try:
            data = pd.read_sql(sql, con=self.db, params=params).to_dict('records')
        except Exception as e:
            raise Exception("pd execute {} failed. the reason {}".format(sql, e))
        return data

    def close_db(self):
        self.db.commit()
        self.cursor.close()
        self.db.close()


class LensRoute:
    def __init__(self, **kwargs):
        """
        :param kwargs:
        ip_port: 元组类型，报警的IP,端口
        code_1,code_2,code_3:报警码
        message: 报警信息
        handle_message : 处理完的报警信息

        :return:
        """
        self.ip_port = kwargs['ip_port']
        self.code_1 = kwargs['code_1']
        self.code_2 = kwargs['code_2']
        self.code_3 = kwargs['code_3']
        self.message = kwargs['message']
        self.alarm_stat = kwargs['alarm_stat']
        self.handle_message = LensRoute.handle_string(self.alarm_stat, self.code_1,
                                                      self.code_2, self.code_3, self.message)

    def socket_send(self):
        try:
            sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 请求连接服务端
            sk.connect(self.ip_port)
        except Exception as e:
            raise Exception(e)

        try:
            # 发送数据 数据格式为00+长度+字符
            sk.send(bytes(self.handle_message, 'GBK'))
        except Exception as e:
            raise Exception(e)

        sk.close()

    @staticmethod
    def handle_string(alarm_stat, code_1, code_2, code_3, message):
        if alarm_stat == "ALARM":
            level = '0|E|'
        else:
            level = '0|N|'
        str1 = level + str(code_1) + '|' + str(code_2) + '|' + str(code_3) + '|' + message.replace('<br>', '；') + '|'
        # 计算转换后的字符长度
        mes = bytes(str1, 'GBK')
        # 表示长度的字符串
        length_str = str(len(mes))
        # 没到4位在开头填充0
        for i in range(4 - len(length_str)):
            length_str = '0' + length_str
        res = length_str + str1
        return res


class SendMsg:
    def __init__(self, title, message, token, url):
        self.title = title
        self.message = message
        self.token = token
        self.url = url

    def send(self):
        parmas = {'message': self.message, 'title': self.title, 'notifyType': 1, 'targetId': self.token,
                  'extParams': ''}
        try:
            result = requests.post(self.url, data=parmas)
            return result.text
        except Exception as e:
            raise Exception(e)


class MailRoute:
    """
        :param kwargs:
        mail_host，mail_user,mail_pass
        header: http header部分
        alert_content: 邮件内容的文字部分 自行生成
        th,tbody tail: 构成表格的元素 可为空 tbody需要自行生成
        subject：邮件标题
        sender：发件人
        receivers：收件人

        :return:
        """
    def __init__(self, **kwargs):
        self.th = None
        self.mail_host = kwargs['mail_host']
        self.mail_user = kwargs['mail_user']
        self.mail_pass = kwargs['mail_pass']
        self.header = kwargs['header']
        self.alert_content = kwargs['alert_content']
        self.subject = kwargs['subject']
        self.sender = kwargs['sender']
        self.receivers = kwargs['receivers']

    def do_send_mail(self, th='', tbody='', tail='', attach_path='', attach_name=''):
        """

        :param attach_path:
        :param th:   表头
        :param tbody:  表格内容
        :param tail:  表格尾部
        :param attach_name:  附件名称
        :return:
        """
        if th:
            mail_msg = self.header + self.alert_content + self.th + tbody + tail
        else:
            mail_msg = self.header + self.alert_content
            # 发送内容定义，utf-8编码，html格式，内容为mail_msg
        context = MIMEText(mail_msg, 'html', 'utf-8')
        message = MIMEMultipart()
        # 发送主题
        # message['From'] =Header('运维监控邮箱', 'utf-8')
        message['From'] = 'yunwei@huifu.com'
        # 邮件接收人
        # message['To'] = Header('报警监控组', 'utf-8').encode()
        message['To'] = ','.join(self.receivers)
        # 邮件标题
        subject = self.subject
        message['Subject'] = Header(subject, 'utf-8')
        message.attach(context)

        if attach_path:
            att = MIMEText(open(attach_path, 'rb').read(), 'base64',
                           'utf-8')
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment; filename=%s' % attach_name
            message.attach(att)

        # 发送邮件
        try:
            # 传送给邮件服务器
            smtp = smtplib.SMTP(self.mail_host, 25)
            # 发送给邮件服务器发件人信息
            smtp.login(self.mail_user, self.mail_pass)
            # 收件人信息
            smtp.sendmail(self.sender, self.receivers, message.as_string())
            # 发送完提示邮件发送成功
        except Exception as e:
            # 打印发送邮件异常
            raise Exception("send email failed the reason:{}".format(e))

