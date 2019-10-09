from setuptools import setup, find_packages
# dev steps
# pip install -e .
# to use virtual env 
# source squacapipy_env/bin/activate

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="squacapipy",
    version="0.4",
    author="Jon Connolly",
    author_email="joncon@uw.edu",
    description="A python api wrapper for SQAUC API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pnsn/squacapipy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
