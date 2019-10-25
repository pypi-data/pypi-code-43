"""SPIN is a simple method for non-supervised clustering method.

This package implements both the Side To Side and the Neighborhood method.
"""
from setuptools import setup, find_packages

setup(name="spin-clustering",
      maintainer="otaviocv",
      maintainer_email="otaviocv.deluqui@gmail.com",
      description="SPIN clustering method package.",
      license="MIT",
      version="0.0.1",
      python_requires=">=3.6",
      install_requires=[
          'numpy>=1.16.4'
          'matplotlib>=3.1.0'
          ]
      )
