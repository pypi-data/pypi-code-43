import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Justipy",
    version="0.0.6",
    author="GustavoDenobi",
    author_email="gustavodenobi@gmail.com",
    description="This package is used to write justified or centralized text to images.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GustavoDenobi/Justipy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)