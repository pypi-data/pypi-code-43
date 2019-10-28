import os
from setuptools import setup
from setuptools import find_packages
from codecs import open
from os import path

# Version
with open(os.path.join("drf_request_client", 'VERSION')) as version_file:
    version = version_file.read().strip()

# Readme contents as description
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='drf-request-client',
    version=version,
    description='Client wrapper for a DRF',
    url='https://aerobotics.com',
    author='Aerobotics',
    author_email='adam@aerobotics.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'urllib3~=1.22',
        'requests>=2.18.4,<3.0.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
    ],
    keywords='api request django rest framework',
    python_requires='>=3.5',
)
