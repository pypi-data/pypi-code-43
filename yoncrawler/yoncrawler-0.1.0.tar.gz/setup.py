#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
# bumpversion [major|minor|patch] setup.py 
# python setup.py sdist bdist_wheel
# twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# pip install --index-url https://test.pypi.org/simple/ yoncrawler
# twine upload --repository-url https://test.pypi.org/legacy/ --skip-existing dist/* (업데이트용)

from setuptools import setup, find_packages

with open('README.md', 'rb') as readme_file:
    readme = readme_file.read().decode('utf-8')

# with open('HISTORY.md', 'rb') as history_file:
#     history = history_file.read().decode('utf-8')

requirements = [
    'beautifulsoup4',
    'pymongo',
    'requests',
    'tinydb',
]

setup_requirements = [
    'pytest-runner', 
    ]

test_requirements = ['pytest>=3', ]

setup(
    author="Taeoh Kim",
    author_email='kimtaeoh95@gmail.com',
    python_requires='>=3, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="연세대학교의 공지사항을 쉽게 크롤링할 수 있는 패키지입니다.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    # long_description=readme + '\n\n' + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords=['yoncrawler', '연세대', '공지', '크롤러'],
    name='yoncrawler',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'test']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/xodhx4/YonseiNotice',
    version='0.1.0',
    zip_safe=False,
)
