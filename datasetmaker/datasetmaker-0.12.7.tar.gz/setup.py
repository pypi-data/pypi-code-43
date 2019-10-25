import re
import setuptools

VERSION_FILE = 'datasetmaker/__init__.py'

with open(VERSION_FILE) as version_file:
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                      version_file.read(), re.MULTILINE)

if match:
    version = match.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSION_FILE,))

requires = [
    "boto3",
    "botocore",
    "bs4",
    "cerberus",
    "ddf_utils",
    "defusedxml",
    "html5lib",
    "lxml",
    "openpyxl",
    "pandas",
    "pyarrow",
    "requests",
    "unidecode",
]

setuptools.setup(
    name="datasetmaker",
    version=version,
    description="Fetch, transform, and package data.",
    author="Datastory",
    author_email="hej@datastory.org",
    install_requires=requires,
    include_package_data=True,
    packages=setuptools.find_packages(),
)
