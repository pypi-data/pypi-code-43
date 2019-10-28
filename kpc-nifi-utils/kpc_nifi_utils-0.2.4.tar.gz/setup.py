from setuptools import setup, find_packages

setup(
    name='kpc_nifi_utils',
    packages=find_packages(),
    version='0.2.4',
    description='Connector utils and configs for implementing with NIFI',
    author='Praiwan N.',
    author_email='npraiwan@outlook.com',
    license='Apache2',
    url='https://github.com/kingpowerclick/kpc-nifi-utils',
    install_requires=[
        'pymongo',
        'argparse',
        'pytz',
        'snowflake-connector-python',
        'python-tds',
        'pg8000'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3'
    ]
)
