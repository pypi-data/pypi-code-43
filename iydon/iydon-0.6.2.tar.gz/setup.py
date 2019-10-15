#!/usr/bin/env python
# coding: utf-8
'''Set up package Iydon.
'''
import setuptools


with open("README.md", "r") as f:
	long_description = f.read()

setuptools.setup(
	name="iydon",
	version="0.6.2",
	author="Iydon Liang",
	author_email="11711217@mail.sustech.edu.cn",
	license='MIT License',
	description="personal api",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/iydon/iydon",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
	install_requires=[
		'IPython',
		'pip',
		'requests',
	],
	tests_require=[
		'pytest',
		'requests',
	],
)
