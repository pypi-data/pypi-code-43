#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 2019/10/9 0009 14:41 
# @Author : HL 
# @Site :  
# @File : setup.py 
# @Software: PyCharm
from distutils.core import setup

setup(name="crawl-icsgm",
      description="this is backage",
      version="1.0",
      author="HL",
      author_email="hel_1226@sina.com",
      packages=['crawl-icsgm-master','crawl-icsgm-master/insert-data','crawl-icsgm-master/insertICData']
      )
