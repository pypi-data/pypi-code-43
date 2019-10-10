from distutils.core import setup
from setuptools import find_packages


setup(
    name='zaach',
    version='1.0.8',
    packages=find_packages(),
    author="Fabian Topfstedt",
    url="https://bitbucket.org/fabian/zaach",
    license='The MIT Licence',
    package_data={'': ['LICENCE', 'README.md']},
    long_description='A collection of helpers',
    keywords = ['base64url', 'timezone', 'conversion'],
    classifiers = [],
)
