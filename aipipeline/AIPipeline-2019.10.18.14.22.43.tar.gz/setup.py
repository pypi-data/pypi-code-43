#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = 'setup.py'
__author__ = 'JieYuan'
__mtime__ = '18-12-14'
"""
import time
from setuptools import find_packages, setup

# rename
package_name = 'bert4keras'
project_name = 'AIPipeline'
version = time.strftime("%Y.%m.%d.%H.%M.%S", time.localtime())

with open("README.md", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=project_name,
    version=version,
    url='https://github.com/Jie-Yuan/' + project_name,
    keywords=["tool wheel", "yuanjie", 'utils'],
    description=('description'),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='JieYuan',
    author_email='313303303@qq.com',
    maintainer='JieYuan',
    maintainer_email='313303303@qq.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.*']},
    platforms=["all"],
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'],

    # entry_points={'console_scripts': [
    #     'mycli=trainer.mycli:main',
    # ]}

)
