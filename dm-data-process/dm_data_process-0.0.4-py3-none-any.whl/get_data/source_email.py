# coding: utf-8
"""
Created on 2018年6月15日

@author: Damon
"""

import poplib
import email
from email.parser import Parser
from email.header import decode_header
from email.header import Header
import time
import re
from urllib import request
import logging
import random
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


def decode_str(s):  # 解析出中文
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def guess_charset(msg):
    charset = msg.get_charset()  # 先从msg对象获取编码:
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()  # 如果获取不到，再从Content-Type字段获取:
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def get_email_new_word(msg):  # 解析成HTML代码
    word = []
    for par in msg.walk():
        if not par.is_multipart():  # 这里要判断是否是multipart，是的话，里面的数据是无用的，至于为什么可以了解mime相关知识。
            try:
                word.append(par.get_payload(decode=True).decode('utf-8').replace('&nbsp;', ''))  # 解码出文本内容，直接输出来就可以了。
            except:
                print('utf-8不能解码')
                word.append(par.get_payload(decode=True).decode('gbk', "ignore").replace('&nbsp;', ''))
    return word[0]

def send_mail(html, subject, sender_addr, sender_password, smtp_server, smtp_port, receiver_addr):
    msg = MIMEText(html, _subtype='html', _charset='utf-8')
    msg['From'] = formataddr(["数据更新监控", sender_addr])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg['To'] = formataddr(["收件人邮箱昵称", receiver_addr])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['Subject'] = subject  # 邮件的主题，也可以说是标题
    server = smtplib.SMTP(smtp_server, smtp_port)  # 发件人邮箱中的SMTP服务器，端口是25
    server.login(sender_addr, sender_password)  # 括号中对应的是发件人邮箱账号、邮箱密码
    server.sendmail(sender_addr, [receiver_addr, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.quit()  # 这句是关闭连接的意思


def get_email_new(email_ac, password, pop3_server, sta=1):
    email_ac = email_ac  # 输入邮件地址,  口令和POP3服务器地址:damon5178646@sohu.com
    password = password  # 'damon5178646'
    server = poplib.POP3(pop3_server)  # 连接到POP3服务器:pop3.sohu.com
    server.set_debuglevel(1)  # 可以打开或关闭调试信息:
    #  print(server.getwelcome().decode('utf-8'))# 可选:打印POP3服务器的欢迎文字:
    server.user(email_ac)  # 身份认证
    server.pass_(password)
    # print('Messages: %s. Size: %s' % server.stat())# stat()返回邮件数量和占用空间:
    resp, mails, octets = server.list()  # list()返回所有邮件的编号:
    # 可以查看返回的列表类似[b'1 82923',  b'2 2184',  ...]
    index = len(mails)  # 获取最新一封邮件,  注意索引号从1开始:
    if index > 0:
        resp, lines, octets = server.retr(index)  # lines存储了邮件的原始文本的每一行,
        msg_content = b'\n'.join(lines).decode()  # 可以获得整个邮件的原始文本:
        msg = email.message_from_string(msg_content)
        msg = Parser().parsestr(msg_content)  # 稍后解析出邮件:
        subject = decode_str(msg.get("Subject"))  # 解析出中文
        From = decode_str(msg.get("From"))  # 解析出中文
        if sta == 1:
            server.dele(index)  # 删除邮件
    else:
        msg = ''
    server.quit()  # 关闭连接:
    return msg, index, subject, From


def get_email_new_ft(date, ac, path, msg):  # 将附件下载到本地path
    name_t = 1
    for par in msg.walk():
        if not par.is_multipart():  # 这里要判断是否是multipart，是的话，里面的数据是无用的，至于为什么可以了解mime相关知识。
            name = par.get_param("name")  # 如果是附件，这里就会取出附件的文件名
            if name:
                # 有附件
                # 下面的三行代码只是为了解码象=?gbk?Q?=CF=E0=C6=AC.rar?=这样的文件名
                h = Header(name)
                dh = decode_header(h)
                fname = dh[0][0]
                # print ('附件名:',  fname)
                data = par.get_payload(decode=True)  # 解码出附件数据，然后存储到文件中
                try:
                    f = open(path + date + '_' + ac + '_' + str(fname.decode()), 'wb')  # 注意一定要用wb来打开文件，因为附件一般都是二进制文件
                except:
                    # print ('附件名有非法字符，自动换一个')
                    f = open(path + date + '_' + ac + '.xlsx', 'wb')
                f.write(data)
                f.close()
            else:
                name_t = 0
    return name_t


def get_email_new_ft_csv(date, ac, path, msg):  # 将附件下载到本地path
    name_t = 1
    for par in msg.walk():
        if not par.is_multipart():  # 这里要判断是否是multipart，是的话，里面的数据是无用的，至于为什么可以了解mime相关知识。
            name = par.get_param("name")  # 如果是附件，这里就会取出附件的文件名
            if name:
                # 有附件
                # 下面的三行代码只是为了解码象=?gbk?Q?=CF=E0=C6=AC.rar?=这样的文件名
                h = Header(name)
                dh = decode_header(h)
                fname = dh[0][0]
                print('附件名:', fname)
                data = par.get_payload(decode=True)  # 解码出附件数据，然后存储到文件中
                try:
                    f = open(path + date + '_' + ac + '_' + str(fname.decode()), 'wb')  # 注意一定要用wb来打开文件，因为附件一般都是二进制文件
                except:
                    print('附件名有非法字符，自动换一个')
                    f = open(path + date + '_' + ac + '.csv', 'wb')
                f.write(data)
                f.close()
            else:
                name_t = 0
    return name_t


def get_url_excel(url, path, name):
    with request.urlopen(url) as web:
        with open(path + name, 'wb') as outfile:  # 为保险起见使用二进制写文件模式，防止编码错误
            outfile.write(web.read())
