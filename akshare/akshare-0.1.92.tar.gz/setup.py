# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
Author: Albert King
date: 2019/10/16 13:58
contact: jindaxiang@163.com
desc: 库基本信息文件
"""
import re
import ast

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version_string():
    """
    get the akshare version number
    :return: str version number
    """
    with open("akshare/__init__.py", "rb") as f:
        version_line = re.search(
            r"__version__\s+=\s+(.*)", f.read().decode("utf-8")
        ).group(1)
        return str(ast.literal_eval(version_line))


setuptools.setup(
    name="akshare",
    version=get_version_string(),
    author="Albert King",
    author_email="jindaxiang@163.com",
    license="MIT",
    description="a tools for downloading financial data!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jindaxiang/akshare",
    packages=setuptools.find_packages(),
    install_requires=[
        "bs4>=0.0.1",
        "lxml>=4.4.1",
        "matplotlib>=3.1.1",
        "pandas>=0.25.1",
        "requests>=2.22.0",
        "demjson>=2.2.4"
    ],
    package_data={'': ['*.py', '*.json', "*.pk"]},
    keywords=['futures finance spider quant quantitative investment trading algotrading'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.7',
)
