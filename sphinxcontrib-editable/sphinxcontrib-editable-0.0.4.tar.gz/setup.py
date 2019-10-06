#!/usr/bin/env python

import setuptools

ns = {}
with open("sphinxcontrib/editable/_version.py") as f:
    exec(f.read(), ns)
VERSION = ns["__version__"]

setuptools.setup(
    name="sphinxcontrib-editable",
    version=VERSION,
    packages=setuptools.find_packages(),
    namespace_packages=["sphinxcontrib"],
    include_package_data=True,
)
