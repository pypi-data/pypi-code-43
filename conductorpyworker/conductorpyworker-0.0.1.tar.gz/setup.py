from setuptools import setup, find_packages

setup(
    name = 'conductorpyworker',
    version = '0.0.1',
    keywords='conductor python sdk',
    description = 'conductor python sdk',
    license = 'MIT License',
    url = '',
    author = 'wyc',
    author_email = '',
    packages = ['conductor'],
    platforms = 'any',
    install_requires = [
        'conductor',
        'requests'
        ],
)