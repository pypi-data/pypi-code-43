from setuptools import setup, find_packages

NAME = "nanonets"
VERSION = "2.0.0"

REQUIRES = [line.strip() for line in open("requirements.txt").readlines()]

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description="The Nanonets API",
    author_email="support@nanonets.com",
    url="https://nanonets.com",
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description_content_type='text/markdown',
    long_description=long_description,
)