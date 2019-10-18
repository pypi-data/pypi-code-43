import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="blueshift",
    version="1.0.0",
    author="Kaleb McKinney",
    description="Quickly create large amounts of unique serial numbers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mckkaleb/blueshift",
    download_url="https://github.com/mckkaleb/blueshift/archive/1.0.0.tar.gz",
    packages=['blueshift'],
    python_requires='>=3.4',
)