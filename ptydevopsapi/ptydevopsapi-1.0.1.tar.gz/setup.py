try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

config = {
    "keywords": "devops api wrapper",
    "author": "Anton Andersson",
    "description": "A python wrapper for the PIM devops API",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "url": "http://antonandersson.se",
    "download_url": "http://antonandersson.se",
    "author_email": "anton@antonandersson.se",
    "version": "1.0.1",
    "install_requires": ["requests"],
    "packages": ["ptydevopsapi"],
    "name": "ptydevopsapi",
    "classifiers": [
        "Programming Language :: Python :: 3.7",
    ],
}

setup(**config)
