 # -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages
import guang


with open('requirements.txt', encoding='utf-8') as f:
    all_reqs = f.read().split('\n')
install_requires = [x.strip() for x in all_reqs if 'git+' not in x]

with open("README.md", "r", encoding='utf-8') as fr:
    long_description = fr.read()


setup(
       name = "guang" ,
       version=guang.__version__,
       description = " Some tools function" ,

       long_description=long_description,
       author = "K.y" ,
       author_email="beidongjiedeguang@gmail.com",
       url = "https://pypi.org/user/K.y/" ,
       license = "GNU" ,
       packages = find_packages(),
       install_requires=install_requires,
       )