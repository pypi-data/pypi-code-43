#!/usr/bin/env python

import setuptools


setuptools.setup(
    name="sphinxcontrib-editable",
    version="0.0.3",
    packages=setuptools.find_packages(),
    namespace_packages=['sphinxcontrib'],
    include_package_data=True,
)
