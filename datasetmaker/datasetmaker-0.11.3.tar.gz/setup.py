import setuptools

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
    version="0.11.3",
    description="Fetch, transform, and package data.",
    author="Robin Linderborg",
    author_email="robin@datastory.org",
    install_requires=requires,
    include_package_data=True,
    packages=setuptools.find_packages(),
)
