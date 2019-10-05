# coding: utf-8

from setuptools import setup, find_packages
import imp
import json
from os import path

_version = imp.load_source("semvergen._version", "semvergen/_version.py")

with open("README.md", "r") as fh:
    long_description = fh.read()

here = path.abspath(path.dirname(__file__))
requires = []

with open(path.join(here, "Pipfile.lock"), "r") as p:
    lock_file = json.loads(p.read())

    default = lock_file['default']

    for key in default.keys():
        requires.append('%s%s' % (key, default[key]['version']))

setup(
    name='semvergen',
    version=_version.__version__,
    description="Semver Generator from Git tags",
    author_email="brad.janke@gmail.com",
    author="Brad Janke",
    url="https://github.com/bradj/semvergen",
    keywords=["semver", "generator"],
    install_requires=requires,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    long_description=long_description,
    scripts=['semvergen/bin/semvergen'],
    data_files=[('./', ['Pipfile.lock'])],
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Code Generators"
    )
)
