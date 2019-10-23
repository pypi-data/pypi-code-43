# pylint: disable=missing-docstring

from setuptools import find_packages, setup

with open("README.rst", "rb") as fp:
    LONG_DESCRIPTION = fp.read().decode("utf-8").strip()

setup(
    name="polarion-docstrings",
    use_scm_version=True,
    url="https://gitlab.com/mkourim/polarion_docstrings",
    description="Reads Polarion docstrings and validates them using flake8",
    long_description=LONG_DESCRIPTION,
    author="Martin Kourim",
    author_email="mkourim@redhat.com",
    license="MIT",
    packages=find_packages(exclude=("tests",)),
    setup_requires=["setuptools_scm"],
    install_requires=["pyyaml", "polarion-tools-common"],
    entry_points={
        "flake8.extension": ["P66 = polarion_docstrings.flake8_plugin:PolarionDocstringsPlugin"]
    },
    keywords=["polarion", "testing"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
    ],
    include_package_data=True,
)
