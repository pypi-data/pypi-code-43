# -*- coding: utf-8 -*-
import os
from codecs import open

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst"), encoding="utf-8") as f:
    README = f.read()
with open(os.path.join(here, "CHANGES.rst"), encoding="utf-8") as f:
    CHANGES = f.read()

requires = [
    "requests",
    "PyYAML",
    "feedgen",
    "simplejson",
    "future",
    "python-stdnum",
    "pytz",
    "zope.interface"
]
extra_requires = {
    "web": [
        "pyramid",
        "colander>=1.7.0",
        "cornice",
        "rfc3987",
    ],
    "redis": [
        "rq",
    ],
    "db": [
        "sqlalchemy",
    ],
    "all": [
        "pyramid",
        "colander>=1.7.0",
        "cornice"
        "rfc3987",
        "rq",
        "sqlalchemy",
    ]
}

setup(
    name="oe_utils",
    version="1.5.0",
    description="Utility Library",
    long_description=README + "\n\n" + CHANGES,
    url="https://github.com/OnroerendErfgoed/oe_utils",
    author="Flanders Heritage Agency",
    author_email="ict@onroerenderfgoed.be",
    license="MIT",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="oe utility",
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    install_requires=requires,
    extra_requires=extra_requires,
    entry_points={},
)
