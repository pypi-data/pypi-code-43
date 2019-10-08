from setuptools import setup
from greenbyte.version import version as gb_version



setup(
    name='mycelium',
    version=gb_version(),
    description='Library for writing dynamic, flexible workflows using python and luigi',
    author='Thomas Winter, Edmund Hood Highcock, Niklas Renström, Pramod Bangalore',
    author_email='thomas@greenbyte.com',
    license='MIT',
    keywords=['workflow', 'pipeline', 'luigi', 'data science'],
    url='http://github.com/greenbyte/mycelium/',
    download_url='http://github.com/greenbyte/mycelium/archive/0.4.5.tar.gz',
    packages=[
        'mycelium',
    ],
    install_requires=[
        'luigi'
        ],
    classifiers=[
    ],
)
