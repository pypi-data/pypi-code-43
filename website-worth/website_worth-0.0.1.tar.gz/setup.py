#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md', encoding='utf-8') as changelog_file:
    changelog = changelog_file.read()

requirements = [
    'Click>=7.0',
    'requests>=2.22',
    'beautifulsoup4>=4.8'
]

setup_requirements = [ ]

test_requirements = [
    "coverage"
]

setup(
    author="Mariusz Korzekwa",
    author_email='maledorak@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Worth of websites calculator",
    entry_points={
        'console_scripts': [
            'website_worth=website_worth.cli:main',
        ],
    },
    python_requires='>=3.5',
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + changelog,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='website_worth',
    name='website_worth',
    packages=find_packages(include=['website_worth']),
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    url='https://github.com/maledorak/website-worth',
    version='0.0.1',
    zip_safe=False,
)
