from setuptools import find_packages
from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='pyutils_dalofeco',
    author='Dalofeco',
    email='me@dalofeco.com',
    description='Standard utility functions for Python 3+',
    long_desription=long_description,
    version='0.2',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
