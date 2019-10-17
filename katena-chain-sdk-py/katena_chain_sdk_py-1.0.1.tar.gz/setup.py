import pathlib
from setuptools import setup, find_packages

# Directory containing this file
HERE = pathlib.Path(__file__).parent

# Text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="katena_chain_sdk_py",
    version="1.0.1",
    description="A SDK client for Katena Chain by Transchain",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/katena-chain/sdk-py",
    author="TransChain",
    author_email="devops@transchain.fr",
    license="Apache-2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(),
    install_requires=['requests==2.22.0', 'pynacl==1.3.0', 'marshmallow==3.2.1'],
    setup_requires=['wheel'],
    include_package_data=True,
)
