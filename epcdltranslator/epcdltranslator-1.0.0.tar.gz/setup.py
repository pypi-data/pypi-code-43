import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="epcdltranslator",
    version="1.0.0",
    author="Ralph Troeger",
    author_email="ralph.troeger@gmail.com",
    description="Translates EPC URIs and EPC Class URIs into their canonical GS1 Digital Link URI equivalents.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RalphTro/gs1-epc-digitallink-translator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
