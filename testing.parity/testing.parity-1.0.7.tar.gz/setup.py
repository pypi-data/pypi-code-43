# -*- coding: utf-8 -*-
from setuptools import setup

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Topic :: Database",
    "Topic :: Software Development",
    "Topic :: Software Development :: Testing",
]

install_requires = [
    'testing.common.database >= 1.1.0',
    'py_ecc',
    'ethereum'
]
tests_require = [
    'nose'
]

setup(
    name='testing.parity',
    version='1.0.7',
    description='automatically setups a parity-ethereum instance, and destroys it after testing',
    long_description=open('README.rst').read(),
    classifiers=classifiers,
    keywords=[],
    author='Tristan King',
    author_email='mail@tristan.sh',
    url='https://github.com/tristan/testing.parity',
    license='Apache License 2.0',
    packages=['testing'],
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    namespace_packages=['testing']
)
