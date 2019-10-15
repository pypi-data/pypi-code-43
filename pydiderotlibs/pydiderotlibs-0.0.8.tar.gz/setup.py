# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os.path
#import pydiderotlib


setupdir = os.path.dirname(__file__)

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = []
for line in open(os.path.join(setupdir, 'requirements.txt'), encoding="UTF-8"):
    if line.strip() and not line.startswith('#'):
        requirements.append(line)

setup(
    name='pydiderotlibs',
    version='0.0.8',
    packages=find_packages(),
    packages_dir = {'' : 'pydiderotlibs'},
    author='Professeurs de Mathématiques du lycée Denis Diderot (Marseille)',
    description="Librairies utilisées dans l'enseignement de l'informatique",
    url='https://github.com/cspaier/pydiderotlibs',
    license='MIT',
    keywords = ["python", "teaching"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Topic :: Education",
    ],
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Active la prise en compte du fichier MANIFEST.in
    include_package_data=True,
    )
