# coding:utf-8

from setuptools import setup

version_file = open("AIMaker/VERSION", "r")
VERSION = version_file.readline()
version_file.close()

setup(
    name='AIMaker',
    version=VERSION,
    description='Return training result to api server',
    author='chris',
    author_email='chris5_lin@asus.com',
    packages=['AIMaker'],
    package_data={'AIMaker': ['VERSION']},
    license='MIT',
    zip_safe=False
)
