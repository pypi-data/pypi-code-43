import os
from setuptools import setup

base_path = os.path.dirname(__file__)

# set the long description
with open(os.path.join(base_path, 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# set requirements
REQUIREMENTS = ['requests']

name = 'dadard_apis_common_pack'
license_name = 'WTFPL'
description = 'package to interact with the Main API of dadard.fr'
git_url = 'http://dadard.fr:8010/dadard/DadardApisCommonPack.git'
version = '1.18'
author_mail = 'florian.charpentier@epita.fr'


setup(
    name=name,
    version=version,
    packages=['CommonPack'],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license=license_name,
    description=description,
    long_description=README,
    url=git_url,
    author='Florian Charpentier',
    author_email=author_mail,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Freeware',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)