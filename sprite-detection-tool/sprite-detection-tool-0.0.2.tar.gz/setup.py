import setuptools
import pipfile


pf = pipfile.load("./Pipfile")


__author__= "lhoaibao"
__copyright__= "Copyright (C) 2019, lhoaibao"
__credits__= None
__email__= "lehoaibao081999@gmail.com"
__license__= "MIT"
__maintainer__= "lhoaibao"
__version__= "0.0.2"


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sprite-detection-tool",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="An useful detect sprite of image package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/intek-training-jsc/sprite-detection-lhoaibao/tree/master",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'pillow'
    ]
)
