import setuptools

import gravwave

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gravwave",
    version=gravwave.__version__,
    author="J. W. Kennington",
    author_email="JamesWKennington@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JWKennington/gravwave",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ),
)
