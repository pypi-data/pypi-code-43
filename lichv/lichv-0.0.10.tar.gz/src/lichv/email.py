#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
 
class Email:

    def __init__(self, user='xxx', email='yyy@zz.com', pwd='xxx', host='smtp.qq.com', port=465):
        self.user = user
        self.email = email
        self.pwd = pwd
        self.host = host
        self.port = port

    def send(self,send_to,title,content):
        ret=True
        try:
            msg=MIMEText(content,'html','utf-8')
            msg['From']=formataddr([self.user,self.email])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To']=','.join(send_to)              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject']=title                # 邮件的主题，也可以说是标题
     
            server=smtplib.SMTP_SSL(self.host, self.port)  # 发件人邮箱中的SMTP服务器，端口是25
            server.login(self.email, self.pwd)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(self.email,send_to,msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
        except Exception as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            print(str(e))
            ret=False
        return {"state":ret}


if __name__ == "__main__":
    email = Email( user='xxx', email='yyy@zz.com', pwd='xxx', host='smtp.qq.com', port=465)
    mail_msg = """
                <p>Python 邮件发送测试...</p>
                <p><a href="http://www.runoob.com">这是一个链接</a></p>
                """
    resutl = email.send(['zzz@zz.com'],"菜鸟教程发送邮件测试",mail_msg)
    print(resutl)

