import os

from setuptools import setup

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

setup(
    name='akeva',
    version='0.0.3',
    description='akeva is an adapter for the Advania Key Vault - A GCP Secrets Manager with secrets stored in GCS.',
    author='Me',
    author_email='alexanderjb@advania.is',
    license='MIT',
    packages=['akeva'],
    url='https://gitlab.com/advania-analytics/internal-projects/advania-key-vault/akeva-adapter',
    zip_safe=False,
    install_requires=['requests']
)