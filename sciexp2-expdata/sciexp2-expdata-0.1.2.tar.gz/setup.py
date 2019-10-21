#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import

import os
import sys
from distutils.core import setup


def run(base):
    version_file = os.path.join(base, "sciexp2", "expdata", "__init__.py")
    with open(version_file) as f:
        code = compile(f.read(), version_file, 'exec')
        version = {}
        exec(code, {}, version)

    with open(os.path.join(base, ".requirements.txt"), "r") as f:
        reqs = [line[:-1] for line in f.readlines()]

    opts = dict(name="sciexp2-expdata",
                version=version["__version__"],
                description="Experiment data analysis framework for SciExp²",
                long_description="""\
SciExp²-ExpData provides helper functions for easing the workflow of analyzing
the many data output files produced by multiple experiments. The helper
functions simply aggregate the many per-experiment files into a single data
structure that contains all the experiment results (e.g., a pandas data frame).

It works best in combination with SciExp²-ExpDef, which can be used to define
many experiments based on parameter permutations.
""",
                author="Lluís Vilanova",
                author_email="llvilanovag@gmail.com",
                url="https://sciexp2-expdef.readthedocs.io/",
                license="GNU General Public License (GPL) version 3 or later",
                classifiers=[
                    "Development Status :: 3 - Alpha",
                    "Environment :: Console",
                    "Intended Audience :: Science/Research",
                    "License :: OSI Approved :: GNU General Public License (GPL)",
                    "Programming Language :: Python",
                    "Topic :: Scientific/Engineering",
                ],
                packages=["sciexp2", "sciexp2.expdata"],
                install_requires=reqs,
                platforms="any",
    )

    setup(**opts)

if __name__ == "__main__":
    run(os.path.dirname(sys.argv[0]))
