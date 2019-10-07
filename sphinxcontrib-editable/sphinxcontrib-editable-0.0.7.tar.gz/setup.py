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
    install_requires=["sphinx", "sphinx_rtd_theme", "importlib_resources"],
    include_package_data=True,
)
