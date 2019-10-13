import codecs
import os

from setuptools import find_packages, setup


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


VERSION = (0, 0, 2)
version = '.'.join(map(str, VERSION))

setup(
    name="jw-python-quickbooks",
    version=version,
    description="Temporary python-quickbooks fork",
    long_description="Temporary python-quickbooks fork",
    author="John Walker",
    author_email="john@chaosdevs.com",
    url="https://github.com/j-walker23/python-quickbooks",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
      'setuptools',
      'intuit-oauth==1.2.2',
      'rauth>=0.7.1',
      'requests>=2.7.0',
      'six>=1.4.0',
      'python-dateutil',
      'pycparser==2.18'
    ],
    license="MIT license",
    zip_safe=False,
    keywords="python-quickbooks",
    python_requires='~=3.7',
    classifiers=[
      "Development Status :: 4 - Beta",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Natural Language :: English",
      "Programming Language :: Python :: 3.7",
    ],
)
