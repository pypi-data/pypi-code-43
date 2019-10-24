import setuptools
import os

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(
    name="soma",
    version="0.1.29",
    author="Cyfer",
    author_email="luiz.costa@somagrupo.com.br",
    description="Private utility package used by SomaLabs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/somalabs/soma-tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas", "mysql-connector", "numpy",
    'google-cloud-storage'],
)
