# -*- coding: utf-8 -*-
import os

from setuptools import find_packages, setup


def get_readme_content():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as f:
        return f.read()


def get_license_content():
    with open(os.path.join(os.path.dirname(__file__), 'LICENSE'), 'r') as f:
        return f.read()


setup(
    name='mail-relay',
    version='0.1.5',
    description='Just a tool to relay incoming emails over to other mail servers',
    long_description=get_readme_content(),
    long_description_content_type='text/markdown',
    author='Saman Tehrani',
    author_email='samanrtehrani@gmail.com',
    url='https://github.com/samantehrani/mail-relay',
    license='GNU General Public License v3.0',
    package_dir={'': 'src'},
    entry_points={
      'console_scripts': [
        'relay = mail_relay.cli:driver'
      ]
    },
    packages=find_packages(where='src', exclude=('tests')),
    python_requires='>=2.7'
)
