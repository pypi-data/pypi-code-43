# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__version__ = '0.0.2'

__doc__ = 'jandan-cli allow you visit jandan.net via cli'

setup(
    name='jandan-cli',
    version=__version__,
    url='https://github.com/lonycc/jandan-py',
    license='MIT',
    author='lonycc',
    author_email='xcc@163.com',
    description='jandan cli',
    long_description=__doc__,
    install_requires=[
        'grequests',
        'bs4',
        'click',
        'tabulate'
    ],
    python_requires='>=3',
    #tests_require = ['nose'],
    #test_suite = 'nose.collector',
    #py_modules=['grequests'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'jandan-py = jandan_cli.cli:run'
        ]
    },
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Terminals'
    ]
)