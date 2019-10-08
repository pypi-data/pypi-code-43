from setuptools import setup, find_packages

import rawpipe


def read_deps(filename):
    with open(filename) as f:
        deps = f.read().split('\n')
        deps.remove("")
    return deps


setup(name="rawpipe",
      version=rawpipe.__version__,
      description="A collection of camera raw processing algorithms.",
      url="http://github.com/toaarnio/rawpipe",
      author="Tomi Aarnio",
      author_email="tomi.p.aarnio@gmail.com",
      license="MIT",
      packages=find_packages(),
      install_requires=read_deps("requirements.txt"),
      zip_safe=True)
