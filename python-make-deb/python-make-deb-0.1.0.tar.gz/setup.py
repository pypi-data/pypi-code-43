#!/usr/bin/env python

from setuptools import setup

setup(
    name='python-make-deb',
    version='0.1.0',
    include_package_data=True,
    packages=['python_make_deb'],
    author="Hugues Morisset",
    author_email="morisset.hugues@gmail.com",
    description="Generates Debian configuration based on your setup.py",
    package_data={
        "python_make_deb": [
            "resources/debian/control.j2",
            "resources/debian/rules.j2",
            "resources/debian/triggers.j2",
            "resources/debian/changelog.j2",
            "resources/debian/compat.j2"
            ]
        },
    install_requires=[
        'future',
        'Jinja2'
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'python-make-deb = python_make_deb:main',
        ]
    },
)
