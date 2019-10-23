from setuptools import setup, find_packages
import os
import sys

with open('README.rst', encoding='utf-8') as fid:
    long_description = fid.read()

setup(
    name='cngi_prototype',
    version='0.0.3',
    description='casa next generation infrastructure prototype',
    long_description=long_description,
    author='National Radio Astronomy Observatory',
    author_email='casa-feedback@nrao.edu',
    url='https://github.com/casangi/cngi_prototype',
    license='Apache-2.0',
    packages=find_packages(),
    install_requires=['numpy',
                      'dask',
                      'distributed',
                      'pyarrow',
                      'bokeh',
                      'pandas'],
)
