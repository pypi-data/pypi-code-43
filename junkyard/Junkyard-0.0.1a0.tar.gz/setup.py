import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Junkyard",
    version="0.0.1a",
    author="CKD",
    author_email="crushkilldestroy@tuta.io",
    description="A collection of helpers created by and for the author",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crushkilldestroy/Junkyard",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
