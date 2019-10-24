#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages
from distutils.extension import Extension
from Cython.Build import cythonize
extensions = [
    Extension("swdclient", ["swdclient.py"],
              include_dirs=["./"],
              libraries=["./libswd.so",],
              library_dirs=["./"]),
]

setup(
    name = "swdclient",
    version = "0.2.6",
    keywords = ("pip", "iscas","auto",),
    description = "SafeWorking Drive Client SDK",
    long_description = "SafeWorking Drive Client SDK",
    license = "MulanPSL",

    author = "yangguang",
    author_email = "yangguang@iscas.ac.cn",

    packages = find_packages("./"),
    include_package_data = True,
    platforms = "linux",
    install_requires = ["google","protobuf==3.8.0"],
    py_modules=["swdclient","server_pb2"],
    package_dir = {'':'./'},   # 告诉distutils包都在src下

    package_data = {
        # 任何包中含有.txt文件，都包含它
        '': ['*.so'],
    }
    # package_data={"./":"*,so"},
    # data_files=[("./",["libswd.so"])]
    # ext_modules = [Extension("swdclient",["libswd.so"],
    #                          language="c++",
    #     library_dirs=[
    #         "lib"
    #     ]
    # )]
)