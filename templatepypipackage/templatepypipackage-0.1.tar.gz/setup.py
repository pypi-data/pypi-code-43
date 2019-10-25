from setuptools import setup

setup(
    name          = 'templatepypipackage',
    version       = '0.1',
    license       = 'BSD 3-Clause License',
    description   = 'Package to setup a basic PyPI package',
    url           = 'https://github.com/tklijnsma/templatepypipackage.git',
    download_url  = 'https://github.com/tklijnsma/templatepypipackage/archive/v0_1.tar.gz',
    author        = 'Thomas Klijnsma',
    author_email  = 'tklijnsm@gmail.com',
    packages      = ['templatepypipackage'],
    zip_safe      = False,
    tests_require = ['nose'],
    test_suite    = 'nose.collector',
    scripts       = [
        'bin/setup-pypi-package'
        ],
    )
