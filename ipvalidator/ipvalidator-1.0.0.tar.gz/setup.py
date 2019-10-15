import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ipvalidator",
    version="1.0.0",
    author="helloworld1008",
    author_email="rsharma1818@outlook.com",
    description="IPvalidator is a python library that validates unicast IP addresses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/helloworld1008/ipvalidator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)


