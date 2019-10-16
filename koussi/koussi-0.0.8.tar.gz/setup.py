import os
import sys

import setuptools
from setuptools.command.install import install

VERSION = '0.0.8'


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


setuptools.setup(
    name='koussi',
    version=VERSION,
    description='Secrets koussi',
    url='https://github.com/pavelch/koussi',
    author="Pavel Chernovsky",
    author_email="pchernovsky@gmail.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'certifi',
        'ruamel.yaml',
    ],
    python_requires='>=3.7',
    # cmdclass={
    #     'verify': VerifyVersionCommand,
    # }
)
