#!/usr/bin/env python

# This will try to import setuptools. If not here, it fails with a message
import os

pre_version = "0.1.2"
if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
else:
    if os.environ.get('CI_JOB_ID'):
        version = os.environ['CI_JOB_ID']
    else:
        version = pre_version

try:
    from setuptools import setup
except ImportError:
    raise ImportError(
        "This module could not be installed, probably because"
        " setuptools is not installed on this computer."
        "\nInstall ez_setup ([sudo] pip install ez_setup) and try again."
    )

with open('README.md') as f:
    long_description = f.read()

# setup(tests_require=["green"], setup_requires=["pbr"], pbr=True)
setup(
    name='galaxie-viewer',
    version=version,
    description='Python package to display text over templates',
    author='Tuxa',
    author_email='tuxa@rtnp.org',
    license=' GPLv3+',
    packages=['GLXViewer'],
    home_page=' https://gitlab.com/Tuuux/galaxie-viewer',
    url=' https://gitlab.com/Tuuux/galaxie-viewer',
    download_url='https://test.pypi.org/project/galaxie-viewer',
    zip_safe=False,
    description_file='README.md',
    long_description=long_description,
    long_description_content_type='text/markdown; charset=UTF-8',
    keywords="Galaxie utility text format template",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
    ],
    tests_require=["green"]
)
