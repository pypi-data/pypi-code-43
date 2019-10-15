# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="ronpy",
    version="1.2.5",
    keywords=['ronpy'],
    description='python libs',
    license='MIT License',
    url='https://gitee.com/rontian/ronpy',
    author='rontian',
    author_email='i@ronpad.com',
    py_modules=["ronpy"],
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=[],
)