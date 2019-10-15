from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='othertools',
    version='1.0.13',
    packages=['othertools'],
    url='https://github.com/zeuscronos/python-othertools',
    license='Apache 2.0',
    author='Zeus Cronos',
    author_email='noreply@notavailable.com',
    description='Other Tools',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
