import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())


setup(
    name="appveyordist",
    version="1.0.0",
    url="https://github.com/mcfletch/appveyordist",
    license='MIT',

    author="Mike C. Fletcher",
    author_email="mcfletch@vrplumber.com",

    description="Download appveyor build artefacts to project dist",
    long_description=read("README.md"),

    packages=find_packages(exclude=('tests',)),

    install_requires=[
        'requests',
    ],

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': [
            'appveyor-dist = appveyordist.main:main',
        ],
    },
)
