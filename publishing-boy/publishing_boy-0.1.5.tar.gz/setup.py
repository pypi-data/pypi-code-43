#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'Django>=2.2.3']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Przemyslaw Kot",
    author_email='przemyslaw.kot@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Publishing Boy is preparing content for publishing",
    entry_points={
        'console_scripts': [
            'publishing_boy=publishing_boy.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='publishing_boy',
    name='publishing_boy',
    packages=find_packages(include=['publishing_boy', 'publishing_boy.tests',]),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/przemekkot/publishing_boy',
    version='0.1.5',
    zip_safe=False,
)
