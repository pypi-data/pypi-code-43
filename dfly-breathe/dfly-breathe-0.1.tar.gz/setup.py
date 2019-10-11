from setuptools import setup
import os

def read(*names):
    return open(os.path.join(os.path.dirname(__file__), *names)).read()

setup(
    name="dfly-breathe",
    version="0.1",
    description="Dragonfly command API",
    author="Mike Roberts",
    author_email="mike.roberts.2k10@googlemail.com",
    license="LICENSE.txt",
    url="https://github.com/mrob95/Breathe",
    long_description = read("README.md"),
    long_description_content_type='text/markdown',
    packages=["breathe"],
    install_requires=["dragonfly2"],
)

