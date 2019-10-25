from setuptools import find_packages
from setuptools import setup


# Read repository information. This will be used as the package description.
long_description = None
with open("README.md", "r") as fh:
    long_description = fh.read()
assert(long_description is not None)


setup(
    name='xlnet-tensorflow',
    version='1.1.2',
    description='XLNet fork of https://github.com/zihangdai/xlnet with package configuration',
    author='sebisebi',
    author_email='gpirtoaca@gmail.com',
    url='https://github.com/zihangdai/xlnet',
    license='Apache 2.0',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'six',
    ],
    extras_require={
        'tensorflow': ['tensorflow>=1.13.1'],
        'sentencepiece': ['sentencepiece>=0.1.83'],
        'numpy': ['numpy>=1.15.0'],
        'absl-py': ['absl-py>=0.7.0'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
    ],
)
