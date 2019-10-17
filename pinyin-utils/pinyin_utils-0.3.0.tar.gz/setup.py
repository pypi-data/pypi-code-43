# setup.py

import sys, re, pathlib
from setuptools import setup, find_packages

# --- Get the text of README.md
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# --- Get the version number
reVersion = re.compile(r'^__version__\s*=\s*\"(.*)\"')
version = ''
with open('./pinyin_utils.py', encoding='utf8') as fh:
	for line in fh:
		result = reVersion.match(line)
		if result:
			version = result.group(1)
			break

setup(
	name = "pinyin_utils",
	version = version,
	author = "John Deighan",
	author_email = "john.deighan@gmail.com",
	description = "Utilities for handling Chinese pinyin",
	long_description = README,
	long_description_content_type = "text/markdown",
	license="MIT",

	url = "https://github.com/johndeighan/pinyin_utils",
	packages = find_packages(),
	py_modules = ['pinyin_utils','translate','tabdb','englisWords','ChineseDB'],
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		],

	# --- All 3rd party packages required:
	python_requires = '>=3.6',
	)
