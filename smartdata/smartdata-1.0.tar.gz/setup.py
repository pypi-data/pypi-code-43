# -*- coding: utf-8 -*-
import sys

from setuptools import setup
import smartui


if sys.version_info < (3, 0):

    long_description = "\n".join([
        open('README.rst', 'r').read(),
    ])
else:
    long_description = "\n".join([
        open('README.rst', 'r', encoding='utf-8').read(),
    ])

setup(
    name='smartdata',
    version=smartui.get_version(),
    packages=['smartui'],
    zip_safe=False,
    include_package_data=True,
    url='https://www.smartchart.cn',
    license='Apache License 2.0',
    author='JohnYan',
    long_description=long_description,
    author_email='84345999@qq.com',
    description='django admin smartchart theme 后台模板, 占个位先',
    install_requires=['django'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
