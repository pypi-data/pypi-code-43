import os
from m2r import parse_from_file
from setuptools import setup

long_description = ''
if os.path.exists('Readme.md'):
    long_description = parse_from_file('Readme.md')

# This call to setup() does all the work
setup(
    name="ingaia-libs",
    version="0.0.47",
    description="inGaia Python Utility Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://gitlab.ingaia.com.br/operacoes/libs/ingaia-libs",
    author="inGaia Operations",
    author_email="suporte.operacoes@i-value.com.br",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    packages=["ingaia", "ingaia.commons", "ingaia.constants", "ingaia.gcloud",
              "ingaia.request_logger", "ingaia.authentication", "ingaia.api"],
    include_package_data=True,
    install_requires=["google-cloud-firestore", "google-cloud-datastore", "google-cloud-tasks", "google-cloud-storage",
                      "google-cloud-bigquery", "flask", "google-cloud-scheduler", "werkzeug", "decorator",
                      "requests", "pyjwt", "six", "cryptography", "PyYAML", "m2r"],
    entry_points={
        "console_scripts": [
            "ingaia-libs=ingaia.__main__:main",
        ]
    },
)
