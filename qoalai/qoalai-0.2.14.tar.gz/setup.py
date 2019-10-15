from setuptools import setup, find_packages
from qoalai import version

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='qoalai',  
    version=version,  
    description='qoala.id data science team library',  
    long_description=long_description,  
    long_description_content_type='text/markdown',
    author='qoala ai team',  
    packages=["qoalai", "qoalai.landmarks", "qoalai.networks", "qoalai.segmentations", "qoalai.transfer_learning"], 
)
