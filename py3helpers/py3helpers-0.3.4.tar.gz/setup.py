#!/usr/bin/env python
"""Create setup script for pip installation of python_utils"""
########################################################################
# File: setup.py
#  executable: setup.py
#
# Author: Andrew Bailey
# History: 12/09/17 Created
########################################################################

import sys
from timeit import default_timer as timer
from setuptools import setup, find_packages


def main():
    """Main docstring"""
    start = timer()
    extras = {
        'seq_tools': ['pysam>=0.15', 'biopython>=1.68', 'mappy>=2.14']
    }
    setup(
        name="py3helpers",
        version='0.3.4',
        description='Python utility functions',
        url='https://github.com/adbailey4/python_utils',
        author='Andrew Bailey',
        license='MIT',
        setup_requires=["pytest-runner"],
        tests_require=["pytest"],
        author_email='andbaile@ucsc.com',
        packages=find_packages(),
        extras_requre=extras,
        scripts=["py3helpers/bin/merge_methyl_bed_files.py"],
        install_requires=['numpy>=1.14.2',
                          'pandas>=0.23.4',
                          'scikit-learn>=0.19.0',
                          'matplotlib>=2.0.2',
                          'pytest-runner>=2.0',
                          'boto3>=1.9',
                          'pytest>=4.3.1'],
        zip_safe=True
    )

    stop = timer()
    print("Running Time = {} seconds".format(stop-start), file=sys.stderr)


if __name__ == "__main__":
    main()
    raise SystemExit
