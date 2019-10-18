import re

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

version = re.search('^__version__\s*=\s*"(.*)"', open("cognite/seismic/__init__.py").read(), re.M).group(1)

setup(
    name="cognite-seismic-sdk",
    version=version,
    description="A wrapper for the Seismic Datastore API offered by Cognite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["cognite." + p for p in find_packages(where="cognite")],
    python_requires=">=3.6",
    license="Apache",
    url="https://github.com/cognitedata/cognite-seismic-sdk",
    author="Vegard Stikbakke",
    author_email="vegard.stikbakke@cognite.com",
    install_requires=["numpy", "grpcio-tools"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
