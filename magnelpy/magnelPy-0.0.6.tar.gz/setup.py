import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="magnelPy",
    version="0.0.6",
    author="magnelPy",
    author_email="ruben.vancoile@ugent.be",
    description="Python toolbox ea14 research group of Ghent University",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.ugent.be/MagnelPy/MagnelPy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)