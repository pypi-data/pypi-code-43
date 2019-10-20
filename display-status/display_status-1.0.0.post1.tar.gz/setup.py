import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="display_status",
    version="1.0.0-1",
    description="Displays the status of links",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/KingAkeem/display_status",
    author="Akeem King",
    author_email="akeemtlking@gmail.com",
    license="GNU GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(),
    include_package_data=True,
    eager_resources=['display_status_bin.so', 'display_status_bin.h', 'main.go'],
    package_data={
        '': 'display_status_bin.so',
        '': 'display_status_bin.h',
        '': 'main.go'
    }
)

