import os
from setuptools import setup, find_packages

BASEDIR = os.path.dirname(os.path.abspath(__file__))
VERSION = open(os.path.join(BASEDIR, 'VERSION')).read().strip()

BASE_DEPENDENCIES = [
    'wf-gqlpycgen>=0.5.9',
    'requests>=2.21',
    'Jinja2>=2.10',
    'gql>=0.1.0',
    'PyYAML>=3.13',
    'click>=6.7',
    'boto3>=1.9.213'
]

TEST_DEPENDENCIES = [
    'pytest==3.0.6',
    'pytest-cov==2.4.0',
    'pytest-mock==1.5.0',
    'pylint==1.6.5',
    'httpretty==0.8.14'
]

LOCAL_DEPENDENCIES = [
    'tox==2.6.0',
    'tox-pyenv==1.0.3'
]

# allow setup.py to be run from any path
os.chdir(os.path.normpath(BASEDIR))

setup(
    name='wildflower-honeycomb-sdk',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    description='SDK for use with the Wildflower Honeycomb API',
    long_description='Provides uniform access to all aspects of the honeycomb API as well as a direct GraphQL interface for more complex queries.',
    url='https://github.com/WildflowerSchools/wildflower-honeycomb-sdk-py',
    author='optimuspaul',
    author_email='paul.decoursey@wildflowerschools.org',
    install_requires= BASE_DEPENDENCIES,
    tests_require = TEST_DEPENDENCIES,
    extras_require = {
        'test': TEST_DEPENDENCIES,
        'local': LOCAL_DEPENDENCIES
    },
    entry_points={
        'console_scripts': [
            'honeycomb=cli:cli',
        ],
    }
)
