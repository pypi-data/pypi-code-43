# https://setuptools.readthedocs.io/en/latest/setuptools.html

# python3 -m pip install --user --upgrade setuptools wheel
# python3 setup.py sdist bdist_wheel
# python3 -m pip install --user --upgrade twine
# python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Uploading distributions to https://test.pypi.org/legacy/
# Enter your username: [your username]
# Enter your password:
# Uploading example_pkg_your_username-0.0.1-py3-none-any.whl
# 100%|█████████████████████| 4.65k/4.65k [00:01<00:00, 2.88kB/s]
# Uploading example_pkg_your_username-0.0.1.tar.gz
# 100%|█████████████████████| 4.25k/4.25k [00:01<00:00, 3.05kB/s]

# python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-pkg-your-username


import os
import sys

import setuptools
from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

classifiers = [
        #'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics']

sourcefiles = ['pyladder.py']

setuptools.setup(
    name='pyladder',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=False,
    # scripts=['pyladder.py'],
    author='Harald Ujc',
    author_email='harald.ujc@screenpopsoftware.com',
    maintainer='Harald ujc',
    maintainer_email='harald.ujc@screenpopsoftware.com',
    description='A python package for planarity testing and rendering of ladder type graphs',
    classifiers=classifiers,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/haraldujc/pyladder',
    python_requires='>=3.6',
)