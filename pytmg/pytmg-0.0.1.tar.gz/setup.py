from setuptools import setup, find_packages

with open("README.md") as infile:
    long_description = infile.read()

setup(
    name="pytmg",
    version="0.0.1",
    author="Christopher Hart",
    author_email="christopherjhart95@gmail.com",
    description="A Python API client library for Cisco's Transceiver Module Group (TMG) Compatibility Matrix",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChristopherJHart/pytmg",
    packages=find_packages(),
    install_requires=[
        "requests>=2.22.0,<3.0"
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)