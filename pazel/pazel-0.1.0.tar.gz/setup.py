"""Entrypoint for starting with pazel.

Run:

`python setup.py install` to install pazel.
`python setup.py develop` to develop pazel.
`python setup.py test` to run pazel tests.
"""

from setuptools import setup, find_packages

DESCRIPTION = "Generate Bazel BUILD files for a Python project."

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setup(
    name='pazel',
    version='0.1.0',
    author="Tuomas Rintamaki",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="automation",
    url="https://github.com/tuomasr/pazel",
    packages=find_packages(exclude=('sample_app', 'sample_app.foo', 'sample_app.tests')),
    classifiers=[
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['pazel = pazel.app:main']
    },
    test_suite='pazel.tests'
)
