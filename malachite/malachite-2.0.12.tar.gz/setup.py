import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

# This call to setup() does all the work
setup(
    name="malachite",
    version="2.0.12",
    description="A Gene Enrichment Meta-Analysis (GEM) Tool for ToppGene",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ggersh/malachite-final",
    author="Gregory R. Gershkowitz, Zachary B. Abrams, Kevin R. Coombes",
    author_email="kevin.coombes@osumc.edu",
    # license="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["bs4", "mechanize", "requests","lxml","xlrd"],
    entry_points={
        "console_scripts": [
            "malachite=malachite.__main__:main",
        ]
    },
)
