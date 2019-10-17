#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import

import os
import sys
from distutils.core import setup


def run(base):
    version_file = os.path.join(base, "sciexp2", "expdef", "__init__.py")
    with open(version_file) as f:
        code = compile(f.read(), version_file, 'exec')
        version = {}
        exec(code, {}, version) #, global_vars, local_vars)

    with open(os.path.join(base, ".requirements.txt"), "r") as f:
        reqs = [line[:-1] for line in f.readlines()]

    opts = dict(name="sciexp2-expdef",
                version=version["__version__"],
                description="Experiment definition framework for SciExp²",
                long_description="""\
SciExp²-ExpDef (aka *Scientific Experiment Exploration - Experiment Definition*)
provides a framework for defining experiments, creating all the files needed for
them and, finally, executing the experiments.

SciExp²-ExpDef puts a special emphasis in simplifying experiment design space
exploration, using a declarative interface for defining permutations of the
different parameters of your experiments, and templated files for the scripts
and configuration files for your experiments. SciExp²-ExpDef supports various
execution platforms like regular local scripts and cluster jobs. It takes care
of tracking their correct execution, and allows selecting which experiments to
run (e.g., those with specific parameter values, or those that were not
successfully run yet).
""",
                author="Lluís Vilanova",
                author_email="llvilanovag@gmail.com",
                url="https://sciexp2-expdef.readthedocs.io/",
                license="GNU General Public License (GPL) version 3 or later",
                classifiers=[
                    "Development Status :: 5 - Production/Stable",
                    "Environment :: Console",
                    "Intended Audience :: Science/Research",
                    "License :: OSI Approved :: GNU General Public License (GPL)",
                    "Programming Language :: Python",
                    "Topic :: Scientific/Engineering",
                ],
                packages=["sciexp2", "sciexp2.common", "sciexp2.expdef", "sciexp2.expdef.system"],
                package_data={"sciexp2": ["expdef/templates/*.dsc", "expdef/templates/*.tpl"]},
                scripts=["launcher"],
                requires=reqs,
                platforms="any",
    )

    setup(**opts)

if __name__ == "__main__":
    run(os.path.dirname(sys.argv[0]))
