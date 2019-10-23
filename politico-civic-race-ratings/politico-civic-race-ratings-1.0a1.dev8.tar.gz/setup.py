# Imports from python.
import os
from setuptools import find_packages
from setuptools import setup


# Imports from entity.
from raceratings import __version__


REPO_URL = "https://github.com/The-Politico/politico-civic-race-ratings/"

PYPI_VERSION = ".".join(str(v) for v in __version__)

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()


setup(
    name="politico-civic-race-ratings",
    version=PYPI_VERSION,
    packages=find_packages(exclude=["docs", "tests", "example"]),
    license="MIT",
    description="Manage electoral race ratings, the POLITICO way.",
    long_description=README,
    long_description_content_type="text/markdown",
    url=REPO_URL,
    download_url="{repo_url}archive/{version}.tar.gz".format(
        **{"repo_url": REPO_URL, "version": PYPI_VERSION}
    ),
    author="POLITICO Interactive News",
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
    include_package_data=True,
    install_requires=[
        "celery",
        "django",
        "djangorestframework",
        "django-filter",
        "psycopg2-binary",
        "politico-civic-utils",
        "politico-civic-entity",
        "politico-civic-geography",
        "politico-civic-election",
        "politico-civic-government",
        "openpyxl",
        "tqdm",
        "us",
        "us-elections",
    ],
    extras_require={"test": ["pytest"]},
)
