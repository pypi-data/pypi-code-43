"""
jt_package_name Python package is for Joe Tilsed to learn how to write a python package and
upload it onto PyPi. Also to show and teach others how to do it themselves.
---
setup.py is the build script for setuptools.
It tells setuptools about your package (such as the name and version) as well as which code files to include.
"""

import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='jt_package_name',
    version="1.0.0",
    author="Joe Tilsed",
    author_email="Joe@Tilsed.com",
    description="Python Package Template",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://linkedin.com/in/joetilsed/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
	keywords="jt_package_name python"
)


# That's all folks...
