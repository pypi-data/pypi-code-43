import os
from setuptools import setup
from djamail import __version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="djamail",
    version=__version__,
    author="Diogo Freitas",
    author_email="diogolaco@gmail.com",
    description=("A pluggable app to ease the task of creating emails"),
    license="MIT",
    keywords="django mail",
    url="https://github.com/buserbrasil/djamail",
    packages=['djamail'],
    long_description=read('README.md'),
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License', 
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'Django>=1.8.0',
    ],
    include_package_data=True,
    zip_safe=False,
)
