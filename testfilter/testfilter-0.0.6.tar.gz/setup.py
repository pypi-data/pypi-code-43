# -*- coding:utf-8 -*-  
# __auth__ = mocobk
# email: mailmzb@qq.com

import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="testfilter",
    version="0.0.6",
    author="mocobk",
    author_email="mocobk@163.com",
    description="unittest 用例执行过滤， 可选择用例执行环境或用例级别进行过滤",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mocobk/testfilter",
    packages=['testfilter'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)