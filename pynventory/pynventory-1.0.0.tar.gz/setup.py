"""Setup script for Pynventory"""

import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="pynventory",
    version="1.0.0",
    description="Generate a Dokuwiki friendly inventory table of you Linux Servers",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/kufsa/pynventory",
    author="Kuffer Sam",
    author_email="sam@skuffer.org",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["pynventory"],
    include_package_data=True,
    install_requires=[
        "fabric",
    ],
    entry_points={"console_scripts": ["pynventory=pynventory.__main__:main"]},
)