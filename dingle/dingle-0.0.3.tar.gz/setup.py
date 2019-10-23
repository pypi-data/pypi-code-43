#!/usr/bin/env python
from dingle import __VERSION__

long_description = ""

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    pass

sdict = {
    'name': 'dingle',
    'version': __VERSION__,
    'packages': ['dingle',
                 'dingle.core',
                 'dingle.util',
                 'dingle.dingtalk'],
    'zip_safe': False,
    'install_requires': ['six'],
    'author': 'gstianfu',
    'long_description': long_description,
    'url': 'https://github.com/gstianfu/dingle',
    'entry_points': {
        'console_scripts': [
            'dingle=dingle.cmd:main',
        ]
    },
    'classifiers': [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python']
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if __name__ == '__main__':
    setup(**sdict)
