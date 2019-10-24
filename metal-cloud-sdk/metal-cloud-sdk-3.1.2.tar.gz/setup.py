from distutils.core import setup
from setuptools import find_packages

version = '3.1.2'
name = 'metal-cloud-sdk'
url = 'https://github.com/bigstepinc/metal-cloud-sdk-python.git'

setup(
    name=name,
    packages=find_packages(),
    version=version,
    description='SDK for the Metal Cloud infrastructure',
    author='Bigstep Inc.',
    author_email='bsiteam@bigstep.com',
    url=url,
    download_url= url + '/tarball/' + version,
    keywords=["metal", "cloud", "sdk"],
    install_requires = [ 'jsonrpc2-base==1.02', 'future' ],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
    ]
)
