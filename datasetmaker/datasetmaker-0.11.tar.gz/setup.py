import setuptools

requires = [
    "bs4",
    "cerberus",
    "ddf_utils",
    "frame2package",
    "html5lib",
    "lxml",
    "openpyxl",
    "pandas",
    "pyarrow",
    "requests",
]

setuptools.setup(
    name="datasetmaker",
    version="0.11",
    description="Fetch, transform, and package data.",
    author="Robin Linderborg",
    author_email="robin@datastory.org",
    install_requires=requires,
    include_package_data=True,
    packages=setuptools.find_packages(),
)
