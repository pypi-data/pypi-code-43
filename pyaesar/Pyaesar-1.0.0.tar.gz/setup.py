"""
    NEED A COPYRIGHT
"""
from os import path
from setuptools import setup
import setuptools

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Pyaesar',
    version='1.0.0',
    description='Data Parallelized MultiNoded Distributed Interface',
    author='Jamil Gafur, Geoffery Fairchild, Carrie Manore, Katherine Kempfert',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author_email='jamilgafur@gmail.com',
    maintainer='Jamil Gafur',
    maintainer_email='jamilgafur@gmail.com',
    url="https://gitlab.com/jamilggafur/pyaesar",
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=[
        'Pyaesar',
    ],
    install_requires=[
       'mpi4py', 'multiprocess'
    ],
)
