from databases import __version__
from setuptools import setup, find_packages


with open('README.rst', 'r') as rm:
    long_description = rm.read()

setup(
    name='databases.py',
    version=__version__,
    author='kaiyo',
    description='Easily create and manipulate databases with databases.py',
    long_description=long_description,
    url='https://github.com/kaiyoo/databases.py',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
