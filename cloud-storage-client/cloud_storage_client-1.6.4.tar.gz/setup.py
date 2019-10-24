import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "cloud_storage_client",
    version = "1.6.4",
    author = "Pablo Aguirre",
    author_email = "paguirrerubio@gmail.com",
    license = "MIT",
    url = "https://pypi.org/project/cloud-storage-client/",
    packages=['cloud_storage_client'],
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    install_requires=[
        'botocore==1.12.250',
        'boto3==1.9.250',
        'google-api-core==1.14.2',
        'google-cloud-storage==1.19.1',
        'azure==3.0.0',
        'pysftp==0.2.9',
        'ssh-agent-setup==1.0.1'
    ],
)
