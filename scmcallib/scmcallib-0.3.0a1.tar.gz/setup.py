#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import realpath, dirname

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import versioneer

PROJECT_ROOT = dirname(realpath(__file__))

PACKAGE_NAME = "scmcallib"
DESCRIPTION = "Framework for calibrating simple climate models"
KEYWORDS = [
    "calibration",
    "tuning",
    "simple climate model",
    "reduced complexity climate model",
    "data processing",
]
AUTHORS = ["Jared Lewis", "Zebedee Nicholls", "Matthias Mengel"]

AUTHOR_EMAILS = [
    "jared.lewis@climate-energy-college.org",
    "zebedee.nicholls@climate-energy-college.org",
    "matthias.mengel@pik-potsdam.de",
]
URL = "https://gitlab.com/magicc/scmcallib"
LICENSE = "2-Clause BSD License"
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Topic :: Scientific/Engineering :: Atmospheric Science",
]

REQUIREMENTS_INSTALL = [
    "pymc3==3.7",
    "numpy",
    "pyam-iamc>=0.2.0",
    "pandas==0.24.2",  # pyam issue, see https://github.com/IAMconsortium/pyam/issues/245
    "matplotlib>=2.0.0",
    "bayesian-optimization",
    "openscm>=0.1.0a",
    "pymagicc>=2.0.0b4",
    "scikit-learn",
]
REQUIREMENTS_TESTS = ["codecov", "pytest-cov", "pytest>=4.0,<5.0"]
REQUIREMENTS_NOTEBOOKS = ["notebook", "nbval", "expectexception"]
REQUIREMENTS_DOCS = ["sphinx>=1.4,<2.1", "sphinx_rtd_theme", "sphinx-click"]
REQUIREMENTS_DEPLOY = ["twine>=2.0.0", "setuptools>=38.6.0", "wheel>=0.31.0"]
REQUIREMENTS_DEV = [
    *["flake8>=3.7.0", "black"],
    *REQUIREMENTS_TESTS,
    *REQUIREMENTS_NOTEBOOKS,
    *REQUIREMENTS_DOCS,
    *REQUIREMENTS_DEPLOY,
]

REQUIREMENTS_EXTRAS = {
    "docs": REQUIREMENTS_DOCS,
    "tests": REQUIREMENTS_TESTS,
    "notebooks": REQUIREMENTS_NOTEBOOKS,
    "deploy": REQUIREMENTS_DEPLOY,
    "dev": REQUIREMENTS_DEV,
}
with open("README.rst", "r") as readme_file:
    README_TEXT = readme_file.read()


class Scmcallib(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        pytest.main(self.test_args)


cmdclass = versioneer.get_cmdclass()
cmdclass.update({"test": Scmcallib})

setup(
    name=PACKAGE_NAME,
    keywords=KEYWORDS,
    url=URL,
    author=",".join(AUTHORS),
    author_email=",".join(AUTHOR_EMAILS),
    description="Perform calibration for simple climate models",
    long_description=README_TEXT,
    long_description_content_type="text/x-rst",
    classifiers=CLASSIFIERS,
    include_package_data=True,
    packages=find_packages(include=["scmcallib"]),
    test_suite="tests",
    install_requires=REQUIREMENTS_INSTALL,
    extras_require=REQUIREMENTS_EXTRAS,
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    zip_safe=False,
)
