from setuptools import setup, find_packages

setup(
    name='smart-integration-utils',
    version='2.2',
    packages=find_packages(),
    install_requires=[
        'Django>=2.0.7',
        'djangorestframework>=3.8.2',
        'psycopg2-binary>=2.7.4',
        'pytz==2018.4',
        'requests>=2.18.2',
        'six==1.11.0',
        'eventmonitoring-client',
        'config_field',
        'drf-dynamicfieldserializer',
        'pycrypto==2.6.1',
    ],
)
