#!/usr/bin/env python
import os
import sys
from setuptools import setup

# Prepare and send a new release to PyPI
if "release" in sys.argv[-1]:
    os.system("python setup.py sdist")
    os.system("twine upload dist/*")
    os.system("rm -rf dist/linear*")
    sys.exit()

# Load the __version__ variable without importing the package already
exec(open('linear/version.py').read())

setup(name='linear',
      version=__version__,
      description="A straightforward package for linear regression with Gaussian priors.",
      long_description=open('README.rst').read(),
      author='Geert Barentsen',
      author_email='hello@geert.io',
      url='https://barentsen.github.io/linear/',
      license='BSD',
      packages=['linear'],
      include_package_data=True,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering :: Astronomy",
          ],
      )
