from setuptools import setup, find_packages
import subprocess
import re

DEFAULT_VERSION = "0.0.0"


def convert_version(version):
    pattern = re.compile(
        "^[r,v,V,R]{0,1}(?P<main>[0-9\.]+)(\-(?P<post>[0-9]+))?(\-.+)?$")
    ver = pattern.search(version)

    if not ver:
        return DEFAULT_VERSION

    new_ver = ver.group('main')

    if ver.group('post'):
        new_ver += ".post{}".format(ver.group('post'))

    return new_ver



try:
    version = subprocess.check_output(
            'git describe --tags', shell=True).rstrip().decode('utf-8')
except subprocess.CalledProcessError:
    version = DEFAULT_VERSION

version = convert_version(version)

setup(name='pollinghub',
      version=version,
      description='',
      url='https://github.com/cy-arduino/python_polling_hub',
      author='ChihYing_Lin',
      author_email='',
      license='LGPL',
      packages=find_packages(exclude=['tests', 'test_*']),
      zip_safe=False)
