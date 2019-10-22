import os
import sys
import requests
import pypandoc

from setuptools import setup
from meaning.version import __version__

try:
    long_description = pypandoc.convert_file('README.md', 'rst')
    long_description = long_description.replace("\r","")
except OSError as e:
    print("\n\n!!! pandoc not found, long_description is bad, don't upload this to PyPI !!!\n\n")
    import io
    # pandoc is not installed, fallback to using raw contents
    with io.open('README.md', encoding="utf-8") as f:
        long_description = f.read()

setup(
    name = "meaning",
    version = __version__,
    author = "Laugh",
    author_email = 'zhang26162@gmail.com',
    url = "https://github.com/laugh12321/meaning",
    description = 'A terminal bilingual dictionary',
    long_description =  long_description,
    packages=['meaning'],
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts':[
            'meaning=meaning.meaning:RunTerminal'
            ]
        },
    zip_safe=False,
)