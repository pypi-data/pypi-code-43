from setuptools import setup, find_packages
from pynlple import __version__

setup(
    name='pyNlple',
    packages=find_packages(exclude=['scripts']),
    include_package_data=True,
    version=__version__,
    description='NLP procedures in python brought to you by YouScan.',
    author='Paul Khudan',
    author_email='pk@youscan.io',
    company='YouScan Limited',
    url='https://github.com/YouScan/pyNlple',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='pynlple.tests',
)