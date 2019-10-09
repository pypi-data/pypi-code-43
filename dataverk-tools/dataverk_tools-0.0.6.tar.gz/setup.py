from setuptools import setup, find_packages
from os import path
from pathlib import Path

# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

with Path("VERSION").open("r") as fh:
    __version__ = fh.read()

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

setup(
    name="dataverk_tools",
    version=__version__,
    description="Theming and colors for dataverker and python dataviz",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/navikt/dataverk_tools/",
    project_urls={"Github": "https://github.com/navikt/dataverk_tools/"},
    author="Paul Bencze",
    author_email="paulbencze@nav.no",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(),
    package_data={"dataverk_tools": ["data/*.csv.gz", "VERSION"]},
    install_requires=install_requires
)
