#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-CLI.
# @File         : mail
# @Time         : 2019-07-11 17:17
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


import yagmail

yag = yagmail.SMTP(user="qq313303303@163.com", password="8643188a", host='smtp.163.com')


def send_mail(receivers=None, subject=None, contents=None, attachments=None, headers=None):
    yag.send(to=receivers,
             subject=subject,
             contents=contents,  # ['数据报告: \n'],
             attachments=attachments,  # ['./profile.htm', '888_WeChat.ipynb'],
             headers=headers if headers else {'From': 'Watchdog'})


if __name__ == '__main__':
    # send_mail('yuanjie@xiaomi.com')
    import yagmail

    yag = yagmail.SMTP(user="qq313303303@163.com", password="8643188a", host='smtp.163.com')
    yag.send('yuanjie@xiaomi.com',
             subject='数据报告',
             contents=['数据报告: \n'],
             headers={'From': 'Watchdog'})