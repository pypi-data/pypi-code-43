import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sbio",
    version="0.0.6",
    author="Tod Stuber",
    author_email="tod.p.stuber@usda.gov",
    description="Collection of simple bioinformatic tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/USDA-VS/sbio",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)