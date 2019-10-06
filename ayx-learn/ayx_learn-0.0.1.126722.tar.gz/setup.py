# Copyright (C) 2019 Alteryx, Inc. All rights reserved.

"""Setup.py for ayx-learn."""
import os
from distutils.core import setup

from setuptools import find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

module_name = "ayx_learn"


def get_new_version(package):
    """Generate the next version of the package."""
    try:
        exec(open(os.path.join(package, "version.py")).read(), globals())

        # Get the package version from the current check in
        package_base_version_str = __version__  # noqa: F821
        package_split_str = package_base_version_str.split(".")

        package_major = int(package_split_str[0])
        package_minor = int(package_split_str[1])
        package_patch = int(package_split_str[2])

        pipeline_id = os.getenv("CI_PIPELINE_ID") or "0"

        new_version = ".".join(
            [
                str(package_major),
                str(package_minor),
                str(package_patch),
                str(pipeline_id),
            ]
        )

    except Exception as e:
        print(str(e))
        new_version = "0.0.0"

    print("New version: " + new_version)
    return new_version


version = get_new_version(module_name)

with open(os.path.join(module_name, "version.py"), "a") as f:
    f.write('\n__version__ = "%s"' % (version,))

description = "Alpha release of ayx-learn."

requirements = ["pandas==0.24.2", "scikit-learn==0.21.1"]

setup(
    name=module_name,
    version=version,
    author="Alteryx, Inc.",
    author_email="support@alteryx.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.alteryx.com/hamilton/ayx-learn",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=requirements,
)
