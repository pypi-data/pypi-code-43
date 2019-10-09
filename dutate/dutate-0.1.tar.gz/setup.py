try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    with open('README.rst') as readme_file:
        long_description = readme_file.read()
except IOError:
    long_description = 'Python client for dutate.com'

setup(
    name='dutate',
    packages=['dutate'],
    version='0.1',
    long_description=long_description,
    description='Python client for dutate.com',
    author='Doniyor Jurabayev',
    author_email='behconsci@gmail.com',
    url='https://gitlab.com/dutate-plugins/python_client',
    download_url='https://gitlab.com/dutate-plugins/python_client/blob/master/dist/dutate-0.1.tar.gz',
    keywords=['track', 'monitor', 'bug'],
    classifiers=[],
    install_requires=[
        'requests'
    ],
)
