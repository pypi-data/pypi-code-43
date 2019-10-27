# -*- coding: utf-8 -*-
"""
Based on Django's ``setup.py``.
"""

import pathlib

from setuptools import setup, find_packages


# Gets version from django_extensions package
version = __import__('django_markdowner').__version__

# List of required packages
install_requires = ['django>=2', 'markdown2']

# List of keywords
keywords = ['django', 'markdown']

# Long description
long_description = """"""
readme_path = pathlib.Path('README.rst')
# Gets long description from README.rst
if readme_path.exists() and readme_path.is_file():
    long_description = readme_path.read_text()

setup(
    name='django-markdowner',
    version=version,
    description='Markdown to Template builder for Django.',
    long_description=long_description,
    author='LeCuay',
    author_email='suso.becerra98@gmail.com',
    url='https://github.com/LeCuay/django-markdowner',
    license='MIT License',
    platforms=['any'],
    packages=find_packages(),
    install_requires=install_requires,
    project_urls={
        'Source Code': 'https://github.com/LeCuay/django-markdowner',
    },
    tests_require=[
        'Django',
        'Werkzeug',
        'pytest',
        'pytest-django',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
