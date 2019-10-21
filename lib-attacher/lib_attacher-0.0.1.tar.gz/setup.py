import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lib_attacher",
    version="0.0.1",
    author="David Ing",
    author_email="ing.dave@gmail.com",
    description="A simple library for finding a superordinate path and attaching it to the module search path.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adaviding/lib_attacher",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)