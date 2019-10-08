#!/usr/bin/env python

PROJECT = 'micropipes-cli'

# Change docs/sphinx/conf.py too!
__VERSION__="0.3.1"

from setuptools import setup, find_packages

try:
    long_description = open('README.md', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=__VERSION__,

    description='Micropipes cli',
    long_description=long_description,

    author='Richard Holly',
    author_email='rho@optimaideas.com',

    url='https://gitlab.com/aicu/lab/micropipes_cli',

    classifiers=['Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.6',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=['cliff', 'cryptography', 'python-jose', 'certifi'],

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'mpipes = mpipes.main:main'
        ],
        'mpipes': [
            'auth_default = mpipes.auth:AuthDefault',
            'auth_list = mpipes.auth:AuthList',
            'auth_authenticate = mpipes.auth:AuthAuthenticate',
            'auth_info = mpipes.auth:AuthInfo',
            'worker_list = mpipes.worker:WorkerList',
            'job_list = mpipes.job:JobList',
            'job_add = mpipes.job:JobAdd',
            'job_edit = mpipes.job:JobEdit',
            'job_stop = mpipes.job:JobStop',
            'job_start = mpipes.job:JobStart',
            'job_delete = mpipes.job:JobDelete',
        ]
    },

    zip_safe=False,
)