from os.path import abspath, dirname, join
from setuptools import setup

__version__ = "1.0.22"


def read_file(filename):
    """Get the contents of a file"""
    here = abspath(dirname(__file__))
    with open(join(here, filename), encoding="utf-8") as f:
        return f.read()


setup(
    name="hatchbuck",
    version=__version__,
    description="Hatchbuck.com CRM API bindings for Python",
    long_description=read_file("README.rst"),
    packages=["hatchbuck"],
    package_dir={"hatchbuck": "."},
    package_data={"hatchbuck": ["hatchbuck_countries.json"]},
    include_package_data=True,
    keywords=["hatchbuck", "CRM", "API"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    url="https://github.com/vshn/python-hatchbuck",
    author="VSHN AG, Bashar Said",
    author_email="bashar.said@vshn.ch",
    license="BSD",
    python_requires=">=3.5",
    extras_require={"dev": ["tox"]},
    install_requires=["phonenumbers>=8", "pycountry>=1", "requests>=2"],
)
