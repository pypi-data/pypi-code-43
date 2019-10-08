# from distutils.core import setup
from setuptools import setup
import os

plugins = ['plugin/' + i for i in os.listdir('plugin')]

setup(
  name='oiretest',
  version='1.0.0',
  description='retest for OIer',
  long_description='Test your code in terminal. For oier to correct test problem or check the code offline with data.',
  license="MIT Licence",

  url='https://github.com/Kewth/retest',
  author='Kewth',
  author_email='Kewth.K.D@outlook.com',

  package_dir={'retest': 'source'},
  packages=['retest'],
  install_requires=[
    'argparse',
    'pyyaml',
    'colorama',
    'resource',
    'pyxdg',
  ],
  data_files=[
    ('share/retest', ['spj', 'retest.yaml']),
    ('share/retest/plugin', plugins),
    ('bin', ['retest']),
  ],
)
