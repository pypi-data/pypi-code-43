# Created: 10/18/2019
# Author:  Emiliano Jordan,
# Project: settings
import os
from setuptools import setup, find_packages


def read(*file):
    with open(os.path.join(os.path.dirname(__file__), *file)) as f:
        return f.read()


about = {}
exec(read('sejings', '__version__.py'), about)

setup(
    author=about['__author__'],
    author_email=about['__author_email__'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    description=about['__description__'],
    license=about['__licence__'],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    name=about['__name__'],
    packages=find_packages(),
    project_urls={
        'Source': 'https://github.com/EmilianoJordan/Sejings/',
        'Tracker': 'https://github.com/EmilianoJordan/Sejings/issues',
    },
    tests_require=[
        'pytest>=3.5.*',
    ],
    url=about['__url__'],
    version=about['__version__'],
)
