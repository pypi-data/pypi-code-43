import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dateFormatExtractor",
    packages = ["dateFormatExtractor"],
    version="1.0.2",
    author="Albert Ventura-Traveset",
    author_email="albertoventuratraveset@hotmail.com",
    description="This package can extract a specific date format from an iterable object (list, pandas column, etc)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VenturaDev/DateExtractorRepo",
    install_requires=['datetime'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)