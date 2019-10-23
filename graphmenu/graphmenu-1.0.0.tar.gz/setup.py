#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import codecs
import sys

from setuptools import setup,find_packages

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='graphmenu',
    version='1.0.0',
    description='some code',
    url='https://github.com/exclusive1214/Law_ChatBot',
    long_description = read("README.txt"),
    author="BensonKAO",
    author_email="bonson930235@gmail.com",
    install_requires=["psycopg2"],
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ]
)

