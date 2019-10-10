import setuptools

from _version import __version__

import os

if not os.path.exists('README'):
    os.link('README.rst', 'README')

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    # remove newline characters
    install_requires = [p[:-1] for p in fh.readlines()]

setuptools.setup(
    name="openepda",
    version=__version__,
    author="Dzmitry Pustakhod",
    author_email="d.pustakhod@tue.nl",
    description="Implementation of open standards for electronic-photonic design automation",
    keywords='epda data science electronics photonics design automation standard',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="http://openepda.org",
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=install_requires,
)