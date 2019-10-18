"""
Build and install the project.

Uses versioneer to manage version numbers using git tags.
"""
import os
from setuptools import setup, find_packages


NAME = "boule"
FULLNAME = "Boule"
AUTHOR = "Leonardo Uieda"
AUTHOR_EMAIL = "leouieda@gmail.com"
MAINTAINER = AUTHOR
MAINTAINER_EMAIL = AUTHOR_EMAIL
LICENSE = "BSD License"
URL = "https://github.com/fatiando/boule"
DESCRIPTION = "Reference ellipsoids for geodesy, geophysics, and coordinate calculations"
KEYWORDS = ""
# with open("README.rst") as f:
    # LONG_DESCRIPTION = "".join(f.readlines())
LONG_DESCRIPTION = ""

VERSION = "0.0.1a"
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Topic :: Scientific/Engineering",
    "Topic :: Software Development :: Libraries",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "License :: OSI Approved :: {}".format(LICENSE),
]
PLATFORMS = "Any"
PACKAGES = find_packages(exclude=["doc"])
SCRIPTS = []
PACKAGE_DATA = {}
INSTALL_REQUIRES = []
PYTHON_REQUIRES = ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*"

if __name__ == "__main__":
    setup(
        name=NAME,
        fullname=FULLNAME,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        license=LICENSE,
        url=URL,
        platforms=PLATFORMS,
        scripts=SCRIPTS,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        classifiers=CLASSIFIERS,
        keywords=KEYWORDS,
        install_requires=INSTALL_REQUIRES,
        python_requires=PYTHON_REQUIRES,
    )
