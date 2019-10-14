import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="blueshift",
    version="0.0.2",
    author="Kaleb McKinney",
    description="Quickly create large amounts of unique serial numbers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mckkaleb/blueshift",
    download_url="https://github.com/mckkaleb/blueshift/archive/0.0.2.tar.gz",
    packages=['blueshift'],
    python_requires='>=3.4',
    classifiers=[
        'Development Status :: 4 - Beta'
    ]
)