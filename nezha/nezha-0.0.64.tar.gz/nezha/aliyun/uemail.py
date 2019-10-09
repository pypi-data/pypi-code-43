# coding: utf-8

"""
the code passed test with aliyun email and aliyun ecs
适用于部署在阿里云服务器
"""

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple, Union


class Email:
    """
    message = MIMEMultipart()
    # 这个参数可以设置抄送.
    message['Cc'] = ''
    """

    def __init__(self, mail_user: str, mail_pass: str, sender: str = '', mail_host: str = 'smtp.mxhichina.com',
                 port: int = 465):
        """

        :param mail_user: 用户
        :param mail_pass: 密码
        :param sender:
        :param mail_host:
        :param port:
        """
        self.mail_host: str = mail_host
        self.mail_user: str = mail_user
        self.mail_pass: str = mail_pass
        # 启用SSL发信, 端口一般是465, 22 端口阿里云服务器默然禁掉
        self.port: int = port
        self.debuglevel: int = 2
        self.from_addr: str = sender or self.mail_user

    def upload_file(self, filename: str) -> MIMEBase:
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)
            # Add header as key/value pair to attachment part
            if filename.find('/') != -1:
                filename = os.path.split(filename)[-1]
            part.add_header('content-disposition', 'attachment', filename=filename)
            return part

    def _send_email(self, to_addrs: Union[Tuple[str], str], message: str) -> None:
        smtpObj = smtplib.SMTP_SSL(self.mail_host, self.port)
        smtpObj.login(self.mail_user, self.mail_pass)
        smtpObj.set_debuglevel(self.debuglevel)
        to_address = to_addrs.split(',') if isinstance(to_addrs, str) else to_addrs
        smtpObj.sendmail(self.from_addr, to_address, message)  # type: ignore
        smtpObj.quit()

    def send_email(self, title: str, content: str, receivers: Union[Tuple[str], str],
                   subtype: str = 'html', content_is_file: bool = False) -> None:
        """

        :param title:
        :param content:
        :param receivers:
        :param subtype:
        :param content_is_file:
        :return:
        """
        # 内容, 格式, 编码
        if content_is_file:
            with open(content, encoding='utf-8') as f:
                content = f.read()
        message = MIMEText(content, subtype, 'utf-8')
        message['From'] = self.from_addr
        message['To'] = receivers.strip() if isinstance(receivers, str) else receivers  # type: ignore
        message['Subject'] = title
        self._send_email(receivers, message.as_string())

    def send_email_attach(self, title: str, content: str, filename: str, receivers: Union[Tuple[str], str],
                          subtype: str = 'html') -> None:
        message = MIMEMultipart()  # 内容, 格式, 编码
        message['From'] = self.from_addr
        message['To'] = receivers.strip() if isinstance(receivers, str) else receivers  # type: ignore
        message['Subject'] = title
        message.attach(MIMEText(content, subtype, 'utf-8'))
        # Add attachment to message and convert message to string
        message.attach(self.upload_file(filename))
        self._send_email(receivers, message.as_string())

    @staticmethod
    def update_receiver(default: str, *added: str) -> str:
        return ','.join((default, *added))
