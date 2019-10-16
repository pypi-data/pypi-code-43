from setuptools import find_packages, setup
import sys

requirements = [
    'numpy',
    'pandas',
    'pyspark'
]

#public version 0.0.2
version = '0.0.2'

setup(
    name='search-tools',
    version=version,
    author="Michael Klear",
    author_email='fixityourself@fu.com',
    url='https://github.com/AlliedToasters/search-tools/archive/v0.0.1.tar.gz',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements
)
