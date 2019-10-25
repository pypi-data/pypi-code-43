# from distutils.core import setup

# setup(
#     name='hazus',
#     version='0.1',
#     packages=['hazus'],
#     license='Creative Commons Attribution-Noncommercial-Share Alike license',
#     long_description=open('README.md').read(),
# )

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hazus",
    version="0.0.3",
    author="James Raines",
    author_email="jraines521@gmail.com",
    description="FEMA - Hazus Open-Source Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nhrap-dev/hazus.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)