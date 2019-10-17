# coding=utf-8


import setuptools


# Use the README file as the long description
with open("README.md", "r") as fh:
    long_description = fh.read()


# Get the version number from the version number file
with open("../rtapi_version_include.txt") as fh:
    version_number = fh.readline().strip()


setuptools.setup(
    name="freeflyer_runtime_api",
    version=version_number,
    author="a.i. solutions, Inc.",
    author_email="techsupport@ai-solutions.com",
    description="Python interface to the FreeFlyer® Runtime API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://ai-solutions.com/freeflyer/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering"
    ],
)
