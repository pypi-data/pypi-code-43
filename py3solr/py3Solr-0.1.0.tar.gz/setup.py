#!win10_x64 python3.6
# coding: utf-8
# Date: 2019/10/27
# wbq813@foxmail.com
import io
import re

from setuptools import setup, find_packages

with io.open("src/py3Solr/__init__.py", "rt", encoding="utf8") as f:
    file = f.read()
    project = re.search(r'__project__ = "(.*?)"', file).group(1)
    desc = re.search(r'__desc__ = "(.*?)"', file).group(1)
    version = re.search(r'__version__ = "(.*?)"', file).group(1)
    author = re.search(r'__author__ = "(.*?)"', file).group(1)
    email = re.search(r'__author_email__ = "(.*?)"', file).group(1)

setup(
    name=project,
    version=version,
    description=desc,
    author=author,
    author_email=email,
    url="https://github.com/wbq813/py3Solr/",
    project_urls={
        "blog": "http://codeyourlife.cn"
    },
    long_description=open("README.md", "r").read(),
    py_modules=["py3Solr"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Programming Language :: Python :: 3",
    ],
    license="MIT",

    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,

    python_requires='>=3.3',
    install_requires=["requests>=2.9.1"],
    extras_require={"solrCloud": ["kazoo>=2.5.0"]},
)
