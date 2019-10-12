from setuptools import setup, find_packages

import komidl.constants as constants

setup(
    # Application name:
    name="KomiDL",
    # Version number
    version=constants.VERSION,
    description="A downloader for image galleries and pages",
    # Tests
    test_suite="tests",
    # Packages
    packages=find_packages(),

    # Application author details:
    author="Dan Sheng",
    author_email="dnsheng@gmail.com",
    url="https://gitlab.com/dnsheng/komidl",

    # Include additional files into the package
    include_package_data=True,

    license="LICENSE",
    long_description=open("README.rst").read(),

    # Dependencies
    python_requires='>3.7.0',

    # Dependent packages (distributions)
    install_requires=[
        "aiohttp",
        "aiofiles",
        "requests",
        "beautifulsoup4",
        "Pillow",
    ],

    entry_points={
        'console_scripts': [
            'komidl=komidl.__main__:main',
        ],
    },

    classifiers=[
        "Environment :: Console",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: MacOS",
        "Operating System :: Microsoft",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.7",
        "Topic :: Multimedia :: Graphics",
    ],
)
