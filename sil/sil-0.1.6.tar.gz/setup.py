import setuptools

from sil import __name__, __version__

with open("README.md", "r") as fh:
    long_description = fh.read()



setuptools.setup(
    name=__name__,
    version=__version__,
    author="Sumner Magruder",
    author_email="sumner.magruder@zmnh.uni-hamburg.de",
    description="Status indicator inline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/sil/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
