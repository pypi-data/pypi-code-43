import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="autodraft",
    version="0.0.3",
    author="Justin Forth",
    author_email="justinforth@gmail.com",
    description="A small package for the AutoDraft streamlit app as well as working with the NHL's API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/j4th/autodraft_pkg",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)