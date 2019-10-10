#-*- coding:utf-8 -*-
from setuptools import setup, find_packages

long_description=''
with open("FortuneData/README.md") as fp:
    long_description=fp.read()

setup(
        name="FortuneData",
        version="1.0.2",
        author="puwow",
        author_email="qiaoguosong@sina.com.cn",
        description="从Fortune网站获取世界500强数据",
        long_description=long_description,
        long_description_content_type="text/markdown",
        #py_modules=['database','datasource'],
        packages=['FortuneData'],
        install_requires=["peewee","requests","bs4"],
        license="MIT",
        license_file="LICENSE",
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3'
            ],

        )
