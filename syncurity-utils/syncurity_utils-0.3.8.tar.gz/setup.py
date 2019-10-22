#!/usr/bin/env python
""" Syncurity-utils package setup.py """

import os
import sys

from codecs import open

try:
    from setuptools import setup
    from setuptools.command.install import install
except ImportError:
    from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))

about = {}

with open(os.path.join(here, 'syncurity_utils', '__version__.py'), 'r', 'utf-8') as ver:
    exec(ver.read(), about)

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

requires = [
    'validators>=0.12.5',
    'irflow-client>=1.5.10,<1.6',
    'sqlalchemy==1.3.8',
    'SQLAlchemy-Utils==0.34.2',
    'psycopg2==2.8.3'
]


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != 'v' + about['__version__']:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, about['__version__']
            )
            sys.exit(info)

setup(
        name=about['__title__'],
        version=about['__version__'],
        description=about['__description__'],
        long_description=readme,
        packages=['syncurity_utils', 'syncurity_utils.db'],
        author=about['__author__'],
        author_email=about['__author_email__'],
        url='https://github.com/syncurity/syncurity-utils',
        maintainer=about['__author__'],
        maintainer_email=about['__author_email__'],
        keywords='Security SOAR Utilities IR-Flow Automation Orchestration',
        platforms='any',
        package_data={'': ['LICENSE.txt']},
        package_dir={'syncurity_utils': 'syncurity_utils'},
        license=about['__license__'],
        python_requires=">=2.7.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
        install_requires=requires,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Topic :: Security',
            'Natural Language :: English',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
        ],
        cmdclass={
            'verify': VerifyVersionCommand,
        }
)
