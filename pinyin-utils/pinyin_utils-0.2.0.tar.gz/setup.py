# setup.py

import sys, pathlib
from setuptools import setup, find_packages

# --- The directory containing this file
HERE = pathlib.Path(__file__).parent

# --- The text of the README file
README = (HERE / "README.md").read_text()

setup(
	name = "pinyin_utils",
	version = "0.2.0",
	author = "John Deighan",
	author_email = "john.deighan@gmail.com",
	description = "Utilities for handling Chinese pinyin",
	long_description = README,
	long_description_content_type = "text/markdown",
	license="MIT",

	url = "https://github.com/johndeighan/pinyin_utils",
	packages = find_packages(),
	py_modules = ['pinyin_utils','translate'],
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		],

	# --- All 3rd party packages required:
	python_requires = '>=3.6',
	)
