# -*- coding: utf-8 -*-

from setuptools import setup

_NAME = "markdownmail"

setup(
    name=_NAME,
    description="E-mail with text and html content provided with markdown",
    long_description=open("README").read(),
    version="0.6.1",
    author="Yaal Team",
    author_email="contact@yaal.fr",
    keywords="mail markdown yaal",
    url="https://deploy.yaal.fr/hg/" + _NAME,
    packages=[_NAME, _NAME + "/styles"],
    package_data={"": ["default.css"]},
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    license="MIT",
    zip_safe=True,
)
