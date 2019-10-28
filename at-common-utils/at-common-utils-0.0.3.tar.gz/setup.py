import io
from setuptools import setup


with io.open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name='at-common-utils',
    author='at-team',
    author_email='hylinux@126.com',
    url="https://pypi.org/project/at-common-utils",
    long_description=open("README.rst").read(),
    version='0.0.3',  # version
    packages=['atp'],  #
    license="MIT",
    descripiton="At Team commonly packaged kits",
    install_requires=requirements,
)
