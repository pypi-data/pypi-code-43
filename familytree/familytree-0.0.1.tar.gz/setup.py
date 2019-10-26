# coding: utf-8
import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="familytree",
    version="0.0.1",
    author="Bodhi Wang",
    author_email="jyxz5@hotmail.com",
    description="This program creates family tree graphs from a simple text files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tjnh05/familytreemaker",
    packages=setuptools.find_packages(),
    package_data={
        'familytree': ['*.svg','*.txt'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)