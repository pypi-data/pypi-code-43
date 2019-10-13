from os.path import join, dirname
from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


PACKAGE = find_packages()
NAME = "django_autocompleter"
DESCRIPTION = ""
AUTHOR = "Stas Shilov"
AUTHOR_EMAIL = "shilowstanisalw@gamail.com"
URL = "https://github.com/stanley0707/django_autocomleter.git"
VERSION = "0.0.7"
 
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=PACKAGE,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
)