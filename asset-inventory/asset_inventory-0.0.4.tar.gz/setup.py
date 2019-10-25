import asset_inventory

from os import path
from setuptools import setup


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


CLASSIFIERS = [
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Operating System :: OS Independent',
]

setup(name='asset_inventory',
      version=asset_inventory.__version__,
      description=asset_inventory.__description__,
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/muhannadengineer/asset_inventory',
      author='Muhannad Alghamdi',
      author_email='muhannadengineer@gmail.com',
      license='MIT',
      packages=['asset_inventory', 'asset_inventory.models'],
      classifiers=CLASSIFIERS,
      keywords='ansible asset inventory',
      install_requires=['ansible', 'paramiko']
      )
