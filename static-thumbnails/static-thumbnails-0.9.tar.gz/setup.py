#!/usr/bin/env python
from __future__ import unicode_literals
import codecs
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import static_thumbnails


def read_files(*filenames):
    """
    Output the contents of one or more files to a single concatenated string.
    """
    output = []
    for filename in filenames:
        f = codecs.open(filename, encoding='utf-8')
        try:
            output.append(f.read())
        finally:
            f.close()
    return '\n\n'.join(output)


setup(
    name='static-thumbnails',
    version=static_thumbnails.get_version(),
    url='https://github.com/mawilmsen/static-thumbnails',
    description='Extension to easy_thumbnails for Django providing thumbnails from static files',
    long_description=read_files('README.md'),
    long_description_content_type='text/markdown',
    author='Marc-Alexander Wilmsen',
    author_email='wilmsen@valloc.de',
    platforms=['any'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.8;python_version>="3"',
        'pillow;python_version>="3"',
        'easy_thumbnails;python_version>="3"'
    ],
    # cmdclass={'test': DjangoTests},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=False,
)