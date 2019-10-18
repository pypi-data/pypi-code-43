#!/usr/bin/python3
import setuptools

with open('README.md') as fh:
    long_description = fh.read()

setuptools.setup(
    name='videnc',
    version='0.0.1.post2',
    author='Andrew Bryant',
    author_email='abryant288@gmail.com',
    description='A FFMpeg wrapper written in python.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/awkawb/videnc',
    install_requires=['av','python-find'],
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
