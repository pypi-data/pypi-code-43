from setuptools import setup
import os

if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
else:
    version = os.environ['CI_JOB_ID']

setup(
    name='gallilama-helloworld-github',
    version=version,
    description='Hello world to test Gitlab PyPi process from GitHub repo',
    author='gallilama',
    author_email='gallilama@gmail.com',
    license='MIT',
    packages=['hello'],
    zip_safe=False
)
