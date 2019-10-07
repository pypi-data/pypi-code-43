# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="kcp_wrapper",
    version='0.2.15',
    zip_safe=False,
    platforms='any',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    package_data={'': ['*.so']},
    url="https://github.com/dantezhu/kcp_wrapper",
    license="MIT",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="kcp_wrapper",
)
