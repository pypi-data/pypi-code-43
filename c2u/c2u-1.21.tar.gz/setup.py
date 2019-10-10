from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="c2u",  # 这里是pip项目发布的名称
    version="1.21",  # 版本号，数值大的会优先被pip
    keywords=("pip", "CamelToUnderline"),
    description="An feature extraction algorithm",
    long_description="An feature extraction algorithm, improve the FastICA",
    license="MIT Licence",

    url="https://github.com/zhangbo2008/CamelToUnderline",  # 项目相关文件地址，一般是github
    author="zhangbo",
    author_email="15122306087@163.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[ ]  # 这个项目需要的第三方库


)
