#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import

import os
import sys
from distutils.core import setup


def run(base):
    version_file = os.path.join(base, "sciexp2", "exprun", "__init__.py")
    with open(version_file) as f:
        code = compile(f.read(), version_file, 'exec')
        version = {}
        exec(code, {}, version)

    with open(os.path.join(base, ".requirements.txt"), "r") as f:
        reqs = [line[:-1] for line in f.readlines()]

    opts = dict(name="sciexp2-exprun",
                version=version["__version__"],
                description="Experiment execution framework for SciExp²",
                long_description="""\
SciExp²-ExpRun provides a framework for easing the workflow of executing
experiments that require orchestrating multiple processes in local and/or remote
machines.
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
                packages=["sciexp2", "sciexp2.exprun"],
                requires=reqs,
                platforms="any",
    )

    setup(**opts)

if __name__ == "__main__":
    run(os.path.dirname(sys.argv[0]))
