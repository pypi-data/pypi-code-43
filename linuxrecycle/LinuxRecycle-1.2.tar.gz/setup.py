#!/usr/bin/env python
# ====================================================
#   Copyright (C)2019 All rights reserved.
#
#   Author        : Xin-Xin MA
#   Email         : xxmawhu@163.com
#   File Name     : setup.py
#   Created Time  : 2019-09-24 10:51
#   Last Modified : 2019-09-29 12:09
#   Describe      :
#
# ====================================================

from setuptools import setup
from setuptools import find_packages
import core
import subprocess
import sys
import os
def set_crontab():
    path = sys.path[0]
    pr = subprocess.Popen(['crontab', '-l'], stdout=subprocess.PIPE)
    out, err = pr.communicate()
    f = open('tmp.txt', 'w')
    try:
        out = str(out).decode()
        print(out)
    except Exception:
        pass
    f.write(str(out))
    command  = '0 2 * * * cd {}/core; ./auto_clear.py;cd -\n'.format(path)
    if command not in str(out):
        f.write('0 2 * * * cd {}/core; ./auto_clear.py;cd -\n'.format(path))
    f.close() 
    subprocess.Popen(['crontab', 'tmp.txt'])
    try:
        pass
        #os.remove('tmp.txt')
    except OSError:
        pass
set_crontab()
setup(
    name='LinuxRecycle',
    version='1.2',
    author='Xin-Xin Ma',
    packages=find_packages(),
    project_urls={
    'Source': 'https://github.com/xxmawhu/LinuxRecycle',
	},  
    entry_points={
        'console_scripts':['rm=core.main:main', 
            'rm.printDB=core.printDB:main',
            'rm.recover=core.recover:main']
        },
    install_requires=[
        'termcolor',
        ]
)
