# -*- coding: utf-8 -*-
import sys

from setuptools import setup

if sys.version_info < (3, 0):

    long_description = "\n".join([
        open('README.rst', 'r').read(),
    ])
else:
    long_description = "\n".join([
        open('README.rst', 'r', encoding='utf-8').read(),
    ])

setup(
    name='simplepro',
    version='0.2-beta',
    packages=['simplepro'],
    zip_safe=False,
    include_package_data=True,
    url='https://github.com/newpanjing/simpleui',
    license='Apache License 2.0',
    author='panjing',
    long_description=long_description,
    author_email='newpanjing@icloud.com',
    description='django admin theme 后台模板',
    install_requires=['django-simpleui>=3.1', 'django-import-export', 'requests', 'rsa'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
