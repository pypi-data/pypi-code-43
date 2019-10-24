#!usr/bin/python
# -*- coding: utf-8 -*-

"""
Package installation setup
"""

import os
import sys
import subprocess
from setuptools import setup, find_packages


version = '0.1.0a0'
sha = 'Unknown'
package_name = 'frgfm_package'

cwd = os.path.dirname(os.path.abspath(__file__))

try:
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd).decode('ascii').strip()
except Exception:
    pass

if os.getenv('BUILD_VERSION'):
    version = os.getenv('BUILD_VERSION')
elif sha != 'Unknown':
    version += '+' + sha[:7]
print("Building wheel {}-{}".format(package_name, version))

def write_version_file():
    version_path = os.path.join(cwd, 'my_package', 'version.py')
    with open(version_path, 'w') as f:
        f.write("__version__ = '{}'\n".format(version))

write_version_file()

with open('README.md') as f:
    readme = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    # Metadata
    name=package_name,
    version=version,
    author='François-Guillaume Fernandez',
    description='My package',
    long_description=readme,
    long_description_content_type="text/markdown",
    url='https://github.com/frgfm/python_docs',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: English',
    ],
    keywords=['python', 'docs'],

    # Package info
    packages=find_packages(exclude=('test',)),
    zip_safe=True,
    python_requires='>=3.6.0',
    include_package_data=True,
    install_requires=requirements,
    package_data={'': ['LICENSE']}
)
