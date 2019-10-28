import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastemc",
    version="0.0.1",
    author="James Rowland",
    author_email="rowland.208@gmail.com",
    description="FastEMC is a method for dimensionality reduction.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rowland-208/fastemc",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)