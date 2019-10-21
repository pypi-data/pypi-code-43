from setuptools import find_packages, setup

from simiotics.version import VERSION

long_description = ''
with open('README.md') as ifp:
    long_description = ifp.read()

setup(
    name='simiotics',
    version=VERSION,
    packages=find_packages(exclude=['e2e']),
    install_requires=[
        'grpcio>=1.24.1,<2.0.0',
        'grpcio-health-checking>=1.24.1,<2.0.0',
        'protobuf',
    ],
    description='Simiotics Python SDK',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Neeraj Kashyap',
    author_email='neeraj@simiotics.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'simiotics_cli = simiotics.cli:main'
        ],
    },
)
