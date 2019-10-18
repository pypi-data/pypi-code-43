from setuptools import (
    setup,
    find_packages
)
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="anduschain",
    version="1.0.1",
    license='MIT',
    author="andus",
    author_email="kmha@andusdeb.com",
    description="anduschain-python SDK ( web3.py wrapped )",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/anduschain/anduschain-python",
    packages=find_packages(),
    classifiers=[
        # 패키지에 대한 태그
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
