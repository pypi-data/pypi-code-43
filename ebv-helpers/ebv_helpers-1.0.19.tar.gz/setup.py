from setuptools import setup

setup(
    name="ebv_helpers",
    version="1.0.19",
    author_email="yasinmeydan@gmail.com",
    description="helpers functions",
    url="https://github.com/yasinmeydan/ebv_helpers.git",
    packages=['ebv_helpers'],
    install_requires=['elasticsearch==6.0.0',
                      'pika>=1.0.1',
                      'python-dateutil>=2.8.0',
                      'requests>=2.22.0',
                      'pymongo>=3.4.0',
                      'nose>=1.3.7',
                      'flake8>=3.7.8']
)
