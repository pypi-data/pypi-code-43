#!/usr/bin/env python3

""" Template of python3 project. """

from setuptools import setup, find_namespace_packages
import os

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

version = {}
with open('version.py') as fp:
    exec(fp.read(), version)

setup(
    name = 'pyTemplateBath',
    author = 'Stephen Richer',
    author_email = 'sr467@bath.ac.uk',
    url = 'https://github.com/StephenRicher/pyTemplate',
    python_requires = '>=3.3.0',
    install_requires = [],
    scripts = [],
    setup_requires = ['pytest-runner'],
    tests_require = ['pytest'],
    license = 'MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
    ],
    version = version['__version__'],
    description = __doc__,
    long_description = read('README.md'),
    long_description_content_type = 'text/markdown',
    packages = find_namespace_packages(where = 'src'),
    package_dir={'': 'src'},
    zip_safe = False,
)
