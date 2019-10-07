from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt')) as f:
    requirements = f.read().splitlines()

with open(path.join(here, 'requirements-dev.txt')) as f:
    requirements_dev = list(filter(lambda l: len(l) > 2 and l[0:2] != '-r', f.read().splitlines()))

with open(path.join(here, 'VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

setup(
    name='autoseeder-cli',
    version=version,
    description='Autoseeder CLI tool',
    long_description=long_description,

    url='https://cosive.com',
    author='Cosive',
    author_email='info@cosive.com',
    license='Apache 2.0',
    keywords='Autoseeder',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
    ],


    packages=find_packages(exclude=['tests*']),

    install_requires=requirements,

    extras_require={
        'test': requirements_dev
    },

    package_data={
    },

    data_files=[
        ('', ['requirements.txt', 'requirements-dev.txt', 'VERSION'])
    ],

    entry_points={
        'console_scripts': [
            'autoseeder-cli = autoseeder_cli:entry_point',
        ],
    },
)
