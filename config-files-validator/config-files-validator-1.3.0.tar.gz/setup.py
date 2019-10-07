import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="config-files-validator",
    version="1.3.0",
    author="Fredrik Westermark",
    author_email="feffe.westermark@gmail.com",
    description="A validator for json, yaml, and jinja2 files",
    license="MIT",
    keywords="json yaml jinja2 configuration config template templates validator validation",
    url="https://github.com/feffe/config-files-validator",
    packages=["config_files"],
    install_requires=["pyyaml", "jinja2", "toml", "junit-xml"],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Quality Assurance",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "console_scripts": [
            "validate-json-files = config_files.validator:report_valid_json_files",
            "validate-yaml-files = config_files.validator:report_valid_yaml_files",
            "validate-jinja2-files = config_files.validator:report_valid_jinja2_files",
            "validate-toml-files = config_files.validator:report_valid_toml_files",
        ]
    },
    python_requires=">=3.6",
)
