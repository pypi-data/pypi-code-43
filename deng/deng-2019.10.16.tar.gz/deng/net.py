#!/usr/bin/env python
# coding:utf-8
"""网络小工具
功能1：判断一个字符串是否为合法的IPV4地址
作者：dengqingyong
邮箱：yu12377@163.com
时间：2018/7/6 10:11
"""


class NetTools(object):
    """网络小工具类"""

    @staticmethod
    def isip(ipaddr, version=4):
        """判断字符串是否为一个合法的IP地址"""
        if '.' not in ipaddr:
            return False
        elif ipaddr.count('.') + 1 != version:
            return False
        else:
            part_list = ipaddr.split('.')
            for index, value in enumerate(part_list):
                try:
                    value = int(value)
                    if index == 0:
                        if 0 < value <= 255:
                            pass
                        else:
                            return False
                    else:
                        if 0 <= value <= 255:
                            pass
                        else:
                            return False
                except Exception as e:
                    return False
            return True
