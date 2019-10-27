# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
from os import path as os_path
import time
this_directory = os_path.abspath(os_path.dirname(__file__))

# 读取文件内容
def read_file(filename):
    with open(os_path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description

# 获取依赖
def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]

setup(
    name='Terry_toolkit',
    version='0.0.1.6.2.8.5'+str(time.time()),
    description='Terry toolkit',
    author='Terry Chan',
    author_email='napoler2008@gmail.com',
    url='https://terry-toolkit.terrychan.org/zh/master/',
    install_requires=read_requirements('requirements.txt'),  # 指定需要安装的依赖
    # install_requires=[
    #     'beautifulsoup4==4.7.1',
    #     'bs4==0.0.1',
    #     'MagicBaidu==0.0.9',
    #     'requests==2.21.0',
    #     'textrank4zh==0.3'

    # ],
    packages=['Terry_toolkit'])
    # install_requires=[
    #     # asn1crypto==0.24.0
    #     # beautifulsoup4==4.7.1
    #     # bs4==0.0.1
    #     # certifi==2019.3.9
    #     # chardet==3.0.4
    #     # cryptography==2.1.4
    #     # cycler==0.10.0
    #     # docopt==0.6.2
    #     # idna==2.6
    #     # jieba==0.39
    #     # keyring==10.6.0
    #     # keyrings.alt==3.0
    #     # kiwisolver==1.0.1
    #     # matplotlib==3.0.3
    #     # numpy==1.16.2
    #     # pandas==0.24.2
    #     # pipreqs==0.4.9
    #     # PyAudio==0.2.11
    #     # pycrypto==2.6.1
    #     # pygobject==3.26.1
    #     # pyparsing==2.4.0
    #     # python-dateutil==2.8.0
    #     # pytz==2019.1
    #     # pyxdg==0.25
    #     # requests==2.21.0
    #     # scipy==1.2.1
    #     # SecretStorage==2.3.1
    #     # six==1.11.0
    #     # soupsieve==1.9.1
    #     # urllib3==1.24.1
    #     # yarg==0.1.9

    # ],

    #install_requires=['jieba'])

# python3 setup.py sdist
# #python3 setup.py install
# python3 setup.py sdist upload
