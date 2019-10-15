#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

VERSION = '1.0.0'

setup(
    name='django_json_tools',  # 库的名称,一般写成文件夹的名字就可以了 pip install 'XXX'

    version=VERSION,   # 版本，每次发版本都不能重复，每次发版必须改这个地方
    description=(
        '个人工具 用于 django 开发 '   # 一个简介，别人搜索包时候，这个概要信息会显示在在搜索列表中
    ),
    # 这是详细的，一般是交别人怎么用，很多包没写，那么在官网就造成没有使用介绍了
    long_description=open('README.md', 'r', encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author='ingrun',       # 作者
    author_email='ingrun@163.com',
    license='BSD License',
    packages=['django_json_tools'],  # 发布的包名
    # packages=find_packages(),
    platforms=["all"],
    url='https://github.com/ingRun/django_json_tools',   # 这个是连接，一般写github就可以了，会从pipy跳转到这里去
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[              # 这里是依赖列表，表示运行这个包的运行某些功能还需要你安装其他的包
        'django',
    ]
)
