from distutils.core import setup
from setuptools import find_packages


setup(
    name="zaach",
    version="1.0.9",
    packages=find_packages(),
    description="A collection of helpers",
    author="Fabian Topfstedt",
    url="https://bitbucket.org/fabian/zaach",
    license="The MIT Licence",
    package_data={"": ["LICENCE", "README.md"]},
    long_description="A collection of helpers",
    keywords=["base64url", "timezone", "conversion", "math"],
    classifiers=[],
)
