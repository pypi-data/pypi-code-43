import setuptools
from setuptools import find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md", "r") as changelog_file:
    changelog = changelog_file.read()

setuptools.setup(
    name="bdrk",
    version="0.1.4",
    author="basis-ai.com",
    author_email="contact@basis-ai.com",
    description="Client library for Bedrock platform",
    long_description=readme + "\n\n" + changelog,
    long_description_content_type="text/markdown",
    url="https://github.com/basisai/span",
    install_requires=["requests", "six"],
    extras_require={
        "cli": ["Click", "docker", "jsonschema", "pyhcl"],
        "fs": ["redis", "fakeredis", "msgpack"],
    },
    packages=find_packages(),
    package_data={"": ["*.hcl", "README.md", "CHANGELOG.md"]},
    exclude_package_data={"": ["README.md", "CHANGELOG.md"]},
    classifiers=["Programming Language :: Python :: 3"],
    entry_points={"console_scripts": ["bdrk = bedrock_client.bedrock.main:main [cli]"]},
)
