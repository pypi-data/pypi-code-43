import os
import sys

import setuptools
from setuptools.command.install import install


def version() -> str: return "0.0.46"


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != version():
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, version()
            )
            sys.exit(info)


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rikki",
    version=version(),
    author="Sergey Yamshchikov",
    author_email="yamsergey@gmail.com",
    description="A small runner script which allows to run behaviour tests backed by proxy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yamsergey/rikki",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    cmdclass={
        'verify': VerifyVersionCommand,
    },
    entry_points={
        'console_scripts': [
            "rikki = rikki.tools.main:rikki"
        ]
    },
    install_requires=[
        "allure-behave>=2.8.5",
        "allure-python-commons>=2.8.5",
        "Appium-Python-Client>=0.47",
        "behave>=1.2.6",
        "mitmproxy>=4.0.4",
        "selenium>=3.141.0",
        "deepdiff>=4.0.7"
    ]
)
