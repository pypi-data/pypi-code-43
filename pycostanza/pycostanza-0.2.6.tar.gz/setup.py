#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from Cython.Build import cythonize
import numpy as np

with open('README.rst') as readme_file:
    readme = readme_file.read()
with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements_dev.txt') as requirements_dev_file:
    setup_requirements = requirements_dev_file.read()
with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read()

#setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Henrik Ahl",
    author_email='hpa22@cam.ac.uk',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Python version of Costanza",
    entry_points={
        'console_scripts': [
            'pycostanza=pycostanza.cli:main',
        ],
    },

    name='pycostanza',
#    ext_modules=cythonize"'**/*.pyx"),
    include_dirs=[np.get_include()],
    packages=find_packages(),
    #package_dir={'':'pycostanza'},

    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pycostanza',
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitlab.com/slcu/teamHJ/henrik_aahl/pycostanza',
    version='0.2.6',
    zip_safe=False,
)
