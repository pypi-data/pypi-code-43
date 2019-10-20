# -*- coding:utf-8 -*-
"""
@author:gjh
@file:setup.py
@time:2019/10/20 16:51
@desc:
"""

from distutils.core import setup
import setuptools
setup(
    name='jiahao',  # 包的名字
    version='0.0.1',  # 版本号
    description='import package test',  # 描述
    author='gjh',  # 作者
    author_email='g15501215130@163.com',  # 你的邮箱
    url='',  # 可以写github上的地址，或者其他地址
    license='MIT',
    packages=setuptools.find_packages(exclude=['jiahao', 'demo']),  # 包内需要引用的文件夹

    # 依赖包
    # install_requires=[
    #     'numpy',
    #     'torchvision',
    #     'flask',
    # ],
    zip_safe=True,
)

