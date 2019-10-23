#!/usr/bin/env python
from setuptools import setup
from hrep import __version__

setup(
    name = "hrep",
    version = __version__,
    author = "Jonathan Goren",
    author_email = "jonagn@gmail.com",
    description = "Binary files search utility",
    license = "MIT",
    keywords = "grep binary files hex search",
    scripts = ["bin/hrep"],
    packages = ["hrep"],
    install_requires = ["scandir"],
    extras_require = {
        'all': ["tqdm"],
    },
    url = "https://gitlab.com/rekodah/hrep",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
