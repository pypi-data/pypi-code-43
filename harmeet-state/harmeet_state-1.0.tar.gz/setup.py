from setuptools import setup, find_packages

with open("README", 'r') as f:
    long_description = f.read()

setup(
   name='harmeet_state',
   version='1.0',
   description='state module',
   license="MIT",
   long_description=long_description,
   author='harmeet sethi',
   author_email='harmeet.sethi@nokia.com',
   url='',
   packages=find_packages(),
   namespace_packages=['src'],
   zip_safe=False,
)
