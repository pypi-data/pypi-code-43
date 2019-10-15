import os
from setuptools import setup, find_packages

config = {
    "name": "sickdb-client",
    "version": "0.0.4",
    "packages": find_packages(),
    "install_requires": ["requests"],
    "author": "Brian Abelson",
    "author_email": "dev@globally.ltd",
    "description": "Python Client For SickDB's API",
    "url": "http://globally.ltd"
}

setup(**config)
