# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup

version = '0.1.8'

root_dir = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(root_dir, "README.md"), "r", encoding="utf-8") as f:
        long_description = f.read()
except IOError:
    long_description = ""

# init version
version_path = os.path.join(root_dir, 'src', 'db_commuter', 'version.py')
with open(version_path, 'w') as f:
    f.write('__version__ = "{}"\n'.format(version))

setup(
    name="db-commuter",
    version=version,
    description="Database communication manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alex Piskun",
    author_email="piskun.aleksey@gmail.com",
    url="https://github.com/viktorsapozhok/db-commuter",
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    packages=find_packages("src"),
    install_requires=[
        "pandas>=0.24.0",
        "sqlalchemy>=1.3.3",
        "psycopg2-binary>=2.7.7"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
