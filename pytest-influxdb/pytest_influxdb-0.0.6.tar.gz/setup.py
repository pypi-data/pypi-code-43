import os

import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name="pytest_influxdb",
    version='0.0.6',
    author="Strike Team",
    author_email="elenaramyan@workfront.com",
    description="Plugin for influxdb and pytest integration.",
    long_description=read('README.rst'),
    url="",
    packages=['pytest_influxdb'],
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    install_requires=['pytest', 'pytest-xdist', 'influxdb', 'pytest-rerunfailures'],
    entry_points={'pytest11': ['pytest-influxdb-plugin = pytest_influxdb.plugin', ], },
)
