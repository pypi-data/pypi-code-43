import os

import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name="influxdb_pytest_plugin",
    version='0.2.48',
    author="Strike Team",
    author_email="elenaramyan@workfront.com",
    description="Plugin for influxdb and pytest integration.",
    long_description=read('README.rst'),
    url="",
    packages=['influxdb_pytest_plugin'],
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    install_requires=['pytest', 'pytest-xdist', 'influxdb', 'pytest-emoji', 'pytest-rerunfailures'],
    entry_points={'pytest11': ['influxdb-pytest = influxdb_pytest_plugin.influxdb_pytest_plugin', ], },
)
