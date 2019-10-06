#! /usr/bin/env python3

import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


def read(fname):
    return open(os.path.join(here, fname)).read()


with open(os.path.join(here, "yaqd_core", "VERSION")) as version_file:
    version = version_file.read().strip()

extra_files = {"yaqd_core": ["VERSION"]}

setup(
    name="yaqd-core",
    packages=find_packages(exclude=("tests", "tests.*")),
    package_data=extra_files,
    python_requires=">=3.7",
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov"],
    install_requires=["appdirs", "toml"],
    extras_require={
        "docs": ["sphinx", "sphinx-gallery>=0.3.0", "sphinx-rtd-theme"],
        "dev": ["black", "pre-commit", "pydocstyle"],
    },
    version=version,
    description="Core structures for yaq component daemons",
    # long_description=read("README.rst"),
    author="yaq Developers",
    license="LGPL v3",
    url="http://gitlab.com/yaq/yaqd-core-python",
    entry_points={
        "console_scripts": [
            "yaqd-base-daemon=yaqd_core._daemon:BaseDaemon.main",
            "yaqd-base-hardware=yaqd_core.hardware._base:BaseHardwareDaemon.main",
            "yaqd-continuous-hardware=yaqd_core.hardware._continuous:ContinuousHardwareDaemon.main",
        ]
    },
    keywords="spectroscopy science multidimensional hardware",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
    ],
)
