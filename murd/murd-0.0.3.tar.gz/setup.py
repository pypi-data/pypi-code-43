from setuptools import setup, Extension


# read the contents of README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()


setup(
    name='murd',
    version='0.0.3',
    author='musingsole',
    author_email='musingsole@gmail.com',
    description='CDRT LWW-Element-Set Tree-Like Key-Value Store. BINGO!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/musingsole/murd',
    install_requires=["boto3"],
    packages=["murd"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
