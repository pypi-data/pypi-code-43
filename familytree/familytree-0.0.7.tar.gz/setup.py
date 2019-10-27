# coding: utf-8
import setuptools, os

packagename= "familytree"
version = "0.0.7"
path = os.path.join(os.getcwd(),packagename, "README.md")

with open(path, "r", encoding='utf-8') as fh:
    long_description = ''.join(fh.readlines()[:-1])

setuptools.setup(
    name=packagename,
    version=version,
    author="Bodhi Wang",
    author_email="jyxz5@hotmail.com",
    description="This program creates family tree graphs from a simple text files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tjnh05/familytreemaker",
    packages=setuptools.find_packages(),
    package_data={
        'familytree': ['LouisXIVfamily.svg','LouisXIVfamily.txt','README.md'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)