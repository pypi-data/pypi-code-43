# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module: setup
***
"""
# Copyright (C) Smart Arcs Ltd, Enigma Bridge Ltd, registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018

import sys
from setuptools import setup, find_packages
from foxyproxy.version import proxy_version

version = proxy_version

# pypi publishing
# 1. set $HOME/.pypirc
#      [distutils]
#      index-servers =
#          pypi
#
#      [pypi]
#      username: <name>
#      password: <password>
# 2. deactivate  // if there's an active env
# 3. cd pycharmenv3; source bin/activate
# 4. pip3 install --upgrade wheel setuptools twine
# 5. cd <whatever_to>/foxyproxy
# 6. rm -rf dist/*
# 7. python3 setup.py sdist bdist_wheel
# 7a.twine check dist/*
# 8. twine upload dist/<latest>.tar.gz
# 9. you can test it with "pip3 install --upgrade --no-cache-dir foxyproxy"


install_requires = [
    'cryptography>=1.5.2',
    'idna<2.7,>=2.5',
    'requests>=2.11.1',
    'setuptools>=39.0',
    'pem',
    # 'six',
    # 'eventlet',
    'flask',
    'flask_sslify',
    # 'flask_socketio',
    'waitress',
    'urllib3',
    'logbook'
]

if sys.version_info < (3,):
    # install_requires.append('scapy-ssl_tls')
    pass
else:
    # install_requires.append('scapy-python3')
    install_requires.append('future')
    pass

setup(
    name='foxyproxy',
    version=version,
    packages=find_packages(exclude=["test_get.py"]),
    namespace_packages=['foxyproxy'],
    include_package_data=True,
    package_data={'foxyproxy': ['LICENSE']},
    install_requires=install_requires,
    url='http://cloudfoxy.com',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    author='Smart Arcs Ltd (built on an inital code by Enigma Bridge Ltd)',
    author_email='support@smartarchitects.co.uk',
    description='TCP/RESTful proxy for Cloud Foxy - cloud platform for smart cards',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Networking',
        'Topic :: Internet :: Proxy Servers'
    ],
    extras_require={
        # 'dev': dev_extras,
        # 'docs': docs_extras,
    },

    entry_points={
        'console_scripts': [
            'foxyproxy=foxyproxy.__main__:main'
        ],
    }
)
