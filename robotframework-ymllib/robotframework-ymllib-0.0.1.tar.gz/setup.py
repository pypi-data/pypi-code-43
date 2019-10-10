from pathlib import Path
from setuptools import find_packages, setup

path = Path("src", "YamlLib", "version.py")

with open("README.md", "r") as fh:
    long_description = fh.read()

with open(path) as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.strip().split("=")[1].strip(" '\"")
            break
    else:
        version = "0.0.1" 

setup(
    name="robotframework-ymllib",
    version=version,
    description="A Robot Framework library for Yaml files",
    long_description=long_description,
    author="Grazia D'Amico",
    author_email="graziagdamico@gmail.com",
    url="",
    license="MIT",
    keywords="robotframework library yaml yml",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["PyYAML>=5.1.1"],
    zip_safe=False,
    package_dir={"": "src"},
    packages=find_packages("src"),
)
