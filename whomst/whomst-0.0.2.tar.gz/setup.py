import os
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    version="0.0.2",
    name="whomst",
    author="minelminel",
    author_email="ctrlcmdspace@gmail.com",
    short_description="infer Python package requirements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/minelminel/whomst",
    packages=['whomst',],
    entry_points={
        "console_scripts": [
            "whomst=whomst:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">3.0",
)
