from setuptools import setup, find_packages
from comdutils import version

setup(
    name='comdutils',  # Required
    version=version,  # Required
    description='a simple package for computer vision deployment',  # Required
    long_description="a simple package for computer vision deployment",  # Optional
    author='fatchur rahman',  # Optional
    packages=["comdutils"],  # Required
)
