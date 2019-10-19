import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylordeckcodes",
    version="1.0.0",
    author="Bamiji",
    author_email="banji@banjislab.com",
    description="A python implementation for the Legends of Runeterra deck encoder/decoder, originally written in C# by Riot Games.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bamiji/PyLoRDeckCodes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
