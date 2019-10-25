import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="squareknot",
    version="0.0.1",
    author="C. J. Stoneking",
    author_email="cjstoneking@gmail.com",
    description="Connecting the parts of data pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cjstoneking/squareknotß",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
