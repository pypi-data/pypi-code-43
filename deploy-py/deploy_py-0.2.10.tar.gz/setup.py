#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "bumpv==0.3.0",
    "Click>=6.0",
    "docker==4.0.2",
    "Jinja2==2.10.1",
    "pykube-ng[gcp]==19.9.2",
    "pyaml==19.4.1",
    "pyhelm==2.14.3",
    "requests==2.22.0",
]

setup_requirements = []

test_requirements = []

setup(
    author="Kylie Auld",
    author_email='kylie@kylie-a.wtf',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Deploy versioned applications with Docker, Helm and Kubernetes.",
    entry_points={
        'console_scripts': [
            'deploy=deploy_py.cli:deploy',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='deploy_py',
    name='deploy_py',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kylie-a/deploy_py',
    version='0.2.10',
    zip_safe=False,
)
