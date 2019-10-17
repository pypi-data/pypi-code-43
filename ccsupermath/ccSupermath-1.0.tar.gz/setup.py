#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/10/17/017 16:08
# @File : setup.py
# @Author : CC
# @Email:253482579@qq.com
# @Software: PyCharm
# @Version:V 1.0

from distutils.core import setup
setup( name='ccSupermath',#对外我们模块的名字
version='1.0',# 版本号
description='这是第一个对外发布的模块，是测试哦',#描述
author='cc',# 作者
author_email='253482579@qq.com',
py_modules=['ccSupermath.demo1','ccSupermath.demo2']# 要发布的模块
)
