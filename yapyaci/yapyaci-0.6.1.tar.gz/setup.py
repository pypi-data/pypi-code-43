import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="yapyaci",
    version="0.6.1",
    description="Yet Another Python ACI Module",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ohynderi/YaPiAci",
    author="Olivier Hynderick",
    author_email="ohynderi@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    include_package_data=True,
    packages=find_packages(exclude=("test",)),
    install_requires=["websocket-client", "python-http-client"],
)