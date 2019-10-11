# create by fanfan on 2019/5/29 0029
#!/usr/bin/env python
# Learn more: https://github.com/kennethreitz/setup.py
from distutils.core import setup
from setuptools import  find_packages
setup(
    name='rasa_nlu_third',
    version='0.1.4',
    description='rasa nlu模块扩展',
    author='qiufengfeng',
    author_email='544855237@qq.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/fanfanfeng/rasa_nlu_qiu',
    license='LGPL',
    #long_description=open("README.md",encoding='utf-8').read()
)
