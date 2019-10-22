#!/usr/bin/env python
import codecs
import os.path
import re
import sys

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requires = ['click>=0.92.4',
                    'bullet>=2.1.0',
                    'colorama>=0.4.1', 
                    'pyfiglet>=0.8.post1']


# if sys.version_info[:2] == (2, 6):
#     # For python2.6 we have to require argparse since it
#     # was not in stdlib until 2.7.
#     install_requires.append('argparse>=1.1')

#     # For Python 2.6, we have to require a different verion of PyYAML since the latest
#     # versions dropped support for Python 2.6.
#     install_requires.append('PyYAML>=3.10,<=3.13')

#     # Colorama removed support for EOL pythons.
#     install_requires.append('colorama>=0.2.5,<=0.3.9')
# elif sys.version_info[:2] == (3, 3):
#     install_requires.append('PyYAML>=3.10,<=3.13')
#     # Colorama removed support for EOL pythons.
#     install_requires.append('colorama>=0.2.5,<=0.3.9')
# else:
#     install_requires.append('PyYAML>=3.10,<5.2')
#     install_requires.append('colorama>=0.2.5,<0.4.2')


setup_options = dict(
    name='breezecli',
    version=find_version("breezecli", "__init__.py"),
    description='Universal Command Line Environment for Breeze.',
    long_description=read('README.md'),
    author='Breeze',
    url='http://breeze/cli/',
    packages=find_packages(exclude=['tests*']),
    install_requires=install_requires,
    license="Apache License 2.0",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points = {
        'console_scripts': [
            'breeze = breezecli.main:cli',
        ],
    },
    # zip_safe=False
)


setup(**setup_options)