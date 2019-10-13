import sys
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'highcompress'))

install_require = ['requests >= 2.7.0, < 3.0.0','simplejson  >= 3.9.0']
tests_require = ['nose >= 1.3, < 2.0', 'httpretty >= 0.8.10, < 1.0.0']

if sys.version_info < (2, 7):
    tests_require.append('unittest2')
if sys.version_info < (3, 3):
    tests_require.append('mock >= 1.3, < 2.0')

setup(
    name='highcompress',
    version="2.6",
    description='Highcompress API client.',
    author='Himalaya Saxena',
    author_email='himalayasaxena@gmail.com',
    license='MIT',
    long_description='Python pakcage for the compressing images through Highcompress API. Highcompress compresses your images intelligently and efficiently. Read more at https://highcompress.com.',
    url='https://highcompress.com/',

    packages=['highcompress'],
    package_data={
        '': ['LICENSE', 'README.md']
    },

    install_requires=install_require,
    tests_require=tests_require,
    extras_require={'test': tests_require},

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ),
)
