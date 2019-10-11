# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
import os.path

from setuptools import find_packages, setup

root_dir = os.path.abspath(os.path.dirname(__file__))
metadata = {}

about_file = os.path.join(root_dir, "sqreen", "__about__.py")
with open(about_file, "rb") as f:
    exec(f.read(), metadata)

readme_file = os.path.join(root_dir, "README.md")
with open(readme_file, "rb") as f:
    long_description = f.read().decode("utf-8")

setup(
    name="sqreen",
    version=metadata["__version__"],
    description="Sqreen agent to protect Python applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=metadata["__author__"],
    author_email=metadata["__email__"],
    url="https://www.sqreen.com/",
    packages=find_packages(
        exclude=[
            "benchmarks.*", "benchmarks",
            "tests.*", "tests",
        ]
    ),
    package_dir={"sqreen": "sqreen"},
    package_data={"sqreen": ["*.crt", "rules_callbacks/*.html"]},
    include_package_data=True,
    install_requires=["py-mini-racer>=0.1.18", "sq-native>=0.4.4,<1"],
    license=metadata["__license__"],
    zip_safe=False,
    keywords="sqreen",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
    ],
    test_suite="tests",
    tests_require=[],
    entry_points={
        "console_scripts": ["sqreen-start = sqreen.bin.protect:protect"]
    },
)
