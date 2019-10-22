import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setup(
    name="jsondesign",
    version="0.2.0",
    description="A Python 3 library handling JSON schema for mimicking entities design in an OO-fashion",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lasircc/jsondesign",
    author="LAS Team",
    author_email="las@ircc.it",
    license="MIT",
    dependency_links=[],
    install_requires=[
        "attrs==19.1.0",
        "jsonref==0.2",
        "jsonschema==3.0.2",
        "pyrsistent==0.15.4",
        "six==1.12.0",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("tests",)),
)
