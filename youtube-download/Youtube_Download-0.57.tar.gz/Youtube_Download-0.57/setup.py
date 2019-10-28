import os
from setuptools import setup

# base path
from YtApi.common.config_accessor import ConfigAccessor

base_path = os.path.dirname(__file__)

# set the long description
with open(os.path.join(base_path, 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# set requirements
with open(os.path.join(base_path, 'requirements.txt')) as r_file:
    REQUIREMENTS = r_file.read().split('\n')

config = ConfigAccessor.config_access('api')
name = config['name']
license_name = config['license']
description = config['description']
git_url = config['git_url']
version = config['version']
author_mail = config['contact']


setup(
    name=name,
    version=version,
    packages=['YtApi'],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license=license_name,
    description=description,
    long_description=README,
    url=git_url,
    author='Florian Charpentier',
    author_email=author_mail,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: Freeware',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
)