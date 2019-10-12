#!/usr/bin/env python
"""
Packaging for the Longtraceback module.
"""

from distutils.core import setup
import setuptools  # noqa

from os import path
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name = 'longtraceback',
    packages = ['longtraceback', 'styledstrings'],
    version = '1.0.356',
    license='MIT',
    description = 'More information about variables and context within traceback',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = 'Charles Ferguson',
    author_email = 'gerph@gerph.org',
    url = 'https://gitlab.gerph.org/gerph/longtraceback',
    keywords = ['traceback'],
    install_requires= [
        ],
    classifiers= [
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',      # Define that your audience are developers
            'License :: OSI Approved :: MIT License',   # Again, pick a license
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            "Operating System :: OS Independent",
        ],
    python_requires='>=2.7',
)
