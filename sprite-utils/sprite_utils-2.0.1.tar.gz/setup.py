import setuptools

__author__ = "Thinh Nguyen"
__email__ = "thinh.nguyen@f4.intek.edu.vn"
__version__ = "2.0.1"
__license__ = "MIT"
__maintainer__ = "Thinh Nguyen"

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sprite_utils",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="Spriteutil is a package contain SpriteSheet Class that can detect and create a new image contain the original image sprites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/intek-training-jsc/sprite-detection-ndthinh8796",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)