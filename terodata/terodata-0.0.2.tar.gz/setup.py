"""
Packaging instructions
"""

from setuptools import find_packages, setup

with open("README.md") as f:
    README = f.read()

with open("requirements.txt") as f:
    ALL_REQS = f.read().split("\n")

setup(
    name="terodata",
    version="0.0.2",
    description="Python binding for tero-data",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Lobelia Earth",
    author_email="info@lobelia.earth",
    url="https://github.com/isardsat/tero-data",
    # license=LICENSE,
    keywords="",
    packages=find_packages(exclude=("tests")),
    # package_dir={"terodata": "terodata"}, # to uncomment if data to add to the package
    # package_data={"terodata": ["data/*.json"]},# to uncomment if data to add to the package
    install_requires=ALL_REQS,
    include_package_data=True,
)
