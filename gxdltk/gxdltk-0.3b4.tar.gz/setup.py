from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='gxdltk',  # package name
    version='0.3-beta-4',  # version
    description="DeepLearning Toolkit for pytorch",
    author='gawainx',
    author_email='liangyixp@live.cn',
    install_requires=['numpy', 'torch', 'mxnet'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
            "Programming Language :: Python :: 3.7",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
)
