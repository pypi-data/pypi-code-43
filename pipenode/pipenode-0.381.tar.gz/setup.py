#from distutils.core import setup
from setuptools import setup, find_packages
with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='pipenode',
    # packages=['pipenode'],
    packages=find_packages(),
    version='0.381',
    description='A clone of Spotify\'s Luigi library with less features and intended for workflows on a single machine.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='qize.luo',
    author_email='qize.luo@miniso.com',
    url='https://gitee.com/Harlaus/pipenode',
    download_url='https://gitee.com/Harlaus/pipenode/archive/0.5.tar.gz',
    keywords=['python', 'workflow'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
