from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='rdbtool',
    packages=find_packages(),

    version='1.0.1',

    license='MIT',

    install_requires=['dropbox'],

    author='reeve0930',
    author_email='reeve0930@gmail.com',

    url='https://github.com/reeve0930/rdbtool',

    description='A simple tool that controls dropbox files.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='rdbtool rdb db dropbox', 

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6',
    ],
)
