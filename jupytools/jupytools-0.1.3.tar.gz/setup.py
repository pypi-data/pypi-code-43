from setuptools import setup, find_packages

exec(open('jupytools/version.py').read())

setup(
    name='jupytools',
    version=__version__,
    maintainer='devforfu',
    description='A set of utilities making Jupyter development a bit easier',
    long_description=open('README.rst', 'r').read(),
    long_description_content_type='text/x-rst',
    url='https://github.com/devforfu/jupytools',
    download_url='https://github.com/devforfu/jupytools/archive/v0.1.0.tar.gz',
    install_requires=['jupyter'],
    packages=find_packages()
)
