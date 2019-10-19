#!/usr/bin/env python
# coding=utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import zhihu_oauth

with open('README.md', 'rb') as f:
    long_description = f.read().decode('utf-8')

setup(
    name='zhihu_oauth',
    keywords=['zhihu', 'network', 'http', 'OAuth', 'JSON'],
    version=zhihu_oauth.__version__,
    packages=['zhihu_oauth', 'zhihu_oauth.oauth', 'zhihu_oauth.zhcls'],
    url='https://git.7sdre.am/7sDream/zhihu-oauth',
    license='MIT',
    author='7sDream',
    author_email='7seconddream@gmail.com',
    description='尝试解析出知乎官方未开放的 OAuth2 接口，并提供优雅的使用方式，'
                '作为 zhihu-py3 项目的替代者',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'requests>=2.10.0',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
