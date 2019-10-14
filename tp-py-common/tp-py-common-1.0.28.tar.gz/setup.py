from setuptools import setup, find_packages

__version__ = "1.0.28"

entry_points = {}

setup(
    name='tp-py-common',
    version=__version__,
    description='Common code to be used by various tp packages',
    author='TruePill',
    packages=find_packages(),
    entry_points=entry_points,
)