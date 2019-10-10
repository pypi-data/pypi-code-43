#!/usr/bin/env python
from setuptools import setup, find_packages

from converter import VERSION

install_requires = [
    'lxml>=4.0',
    'weasyprint>=0.42.3'
]

tests_require = []

setup(
    name="xconverter",
    version=VERSION,
    description="Library to convert Érudit Article XML's to Érudit Publishing Schema (JATS), HTML and PDF. ",
    author="Érudit",
    author_email="fabio.batalha@erudit.org",
    maintainer="Fabio Batalha",
    maintainer_email="fabio.batalha@erudit.org",
    url="http://github.com/fabiobatalha/converter",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3"
    ],
    dependency_links=[],
    tests_require=tests_require,
    test_suite='tests',
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'converter=converter.console_script:main'
        ]
    }
)
