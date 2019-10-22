import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="python_logger",
    version="0.0.1",
    author="Adam Cincura",
    author_email="cz.data@dtone.com",
    description="Wrapper around standard python logging implementing additional features.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://git.dtone.xyz/data/python_logger",
    packages=setuptools.find_packages(),
    install_requires=[],
    test_suite="nose.collector",
    tests_require=["pytest"],
    classifiers=["Programming Language :: Python :: 3.7"],
    keywords="python logger mdc",
    include_package_data=True,
    zip_safe=False,
)
