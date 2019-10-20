"""Contains all the configuration for the package on pypi/pip.

Functions
---------
concat_description : str
    Reads and yields the content of the filenames.

Module Variables
----------------
long_description : str
    The content in README.md and CHANGELOG.md and used for module description.

Notes
-----
Primary entrypoint is in kuws.command_line_utility.

"""
import setuptools

def concat_description(*filenames):
    """Reads and yields the content of the filenames.

    Arguments
    ---------
    *filenames
        An arbitrary number of filenames to parse

    Yields
    ------
    str:
        The current files content (from file.read() function)

    """
    for current_file in filenames:
        with open(current_file, 'r') as f:
            yield f.read()

# Appending the changelog to the readme for a complete package description
long_description = ""
for content in concat_description("README.md", "CHANGELOG.md"):
    long_description += content

setuptools.setup(
    name="kuws",
    version="0.0.5",
    author="Kieran Wood",
    author_email="kieranw098@gmail.com",
    description="A set of python scripts for common web tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Descent098/kuws",
    packages=setuptools.find_packages(),
    entry_points={
          'console_scripts': ['kuws = kuws.command_line_utility:main']
      },
    install_requires=[
    "requests",
    "pytube",
    "pyopenssl",
    "docopt",
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)