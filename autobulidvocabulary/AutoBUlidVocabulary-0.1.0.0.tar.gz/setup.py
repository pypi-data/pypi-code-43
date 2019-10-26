# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
from os import path as os_path
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
    name='AutoBUlidVocabulary',
    version='0.1.0.0',
    description='Auto BUlid Vocabulary',
    author='Terry Chan',
    author_email='napoler2008@gmail.com',
    url='https://github.com/napoler/AutoBUlidVocabulary',
    #install_requires=read_requirements('requirements.txt'),  # 指定需要安装的依赖
    install_requires=[
        # 'beautifulsoup4==4.7.1',

    ],
    packages=['AutoBUlidVocabulary'])

"""
python3 setup.py sdist
python3 setup.py install
python3 setup.py sdist upload


"""
