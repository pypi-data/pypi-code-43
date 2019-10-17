from setuptools import setup, find_packages

__version__ = "2.0.1"

entry_points = {}

setup(
    name='tp-py-common',
    version=__version__,
    description='Common code to be used by various tp packages',
    author='TruePill',
    packages=find_packages(),
    entry_points=entry_points,
)