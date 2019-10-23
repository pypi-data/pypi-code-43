# Imports from python.
import os
from setuptools import find_packages
from setuptools import setup


# Imports from government.
from government import __version__


REPO_URL = "https://github.com/The-Politico/politico-civic-government/"

PYPI_VERSION = ".".join(str(v) for v in __version__)


setup(
    name="politico-civic-government",
    version=PYPI_VERSION,
    packages=find_packages(exclude=["docs", "tests", "example"]),
    license="MIT",
    url=REPO_URL,
    download_url="{repo_url}archive/{version}.tar.gz".format(
        **{"repo_url": REPO_URL, "version": PYPI_VERSION}
    ),
    author="POLITICO interactive news",
    author_email="interactives@politico.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords="",
    install_requires=[
        "django",
        "djangorestframework",
        "dj-database-url",
        "psycopg2-binary",
        "politico-civic-utils",
        "politico-civic-entity",
        "politico-civic-geography",
        "tqdm",
        "us",
        "us-elections",
    ],
    extras_require={
        "dev": ["sphinx", "sphinxcontrib-django", "sphinx-rtd-theme"],
        "test": ["pytest"],
    },
)
