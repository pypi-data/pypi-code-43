from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()
import os

import setuptools


PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(PACKAGE_ROOT, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(PACKAGE_ROOT, 'requirements.txt')) as f:
    REQUIREMENTS = [r.strip() for r in f.readlines()]


setuptools.setup(
    name='gcloud-rest-bigquery',
    version='3.1.0',
    description='Python Client for Google Cloud BigQuery',
    long_description=README,
    namespace_packages=[
        'gcloud',
        'gcloud.rest',
    ],
    packages=setuptools.find_packages(exclude=('tests',)),
    install_requires=REQUIREMENTS,
    python_requires='>= 2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    author='Vi Engineering',
    author_email='voiceai-eng@dialpad.com',
    url='https://github.com/talkiq/gcloud-rest',
    platforms='Posix; MacOS X; Windows',
    include_package_data=True,
    zip_safe=False,
    license='MIT License',
    classifiers=['Programming Language :: Python :: 2','Programming Language :: Python :: 2.7','Programming Language :: Python :: 3.4','Programming Language :: Python :: 3.5',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet',
    ],
)
