import os
import sys

from setuptools import find_packages, setup
from setuptools.command.install import install

VERSION = "0.1.0"


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)


setup(
    name="cascade_settings",
    version="0.1.0",
    author="Szymon Zareba",
    author_email="szymon.zareba@alphamoon.ai",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        'simple-settings',
    ],
    tests_require=[
        'pytest',
    ],
    python_requires='>=3.6.0',
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
