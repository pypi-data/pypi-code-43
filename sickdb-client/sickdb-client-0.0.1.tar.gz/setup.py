import os
from setuptools import setup, find_packages

reqs = os.path.abspath(os.path.join(os.path.dirname(__file__), "requirements.txt"))
with open(reqs) as f:
    install_requires = [req.strip() for req in f]

config = {
    "name": "sickdb-client",
    "version": "0.0.1",
    "packages": find_packages(),
    "install_requires": install_requires,
    "author": "gltd",
    "author_email": "dev@globally.ltd",
    "description": "Python Client For SickDB's API",
    "url": "http://globally.ltd",
    "install_requires": install_requires
}

setup(**config)
