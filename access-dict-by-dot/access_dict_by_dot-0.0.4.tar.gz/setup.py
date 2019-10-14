from os import path
from distutils.core import setup
from setuptools import setup

long_description = ''
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


print(long_description)


setup(
  name = 'access_dict_by_dot',
  packages = ['access_dict_by_dot'],
  version = '0.0.4',
  license='MIT',
  description = 'Using this packages we can access dictionary values using dot operator',
  type="text",
  author = 'Indrajeet Singh',
  author_email = 'indrajeetsinghmaan@gmail.com',
  url = 'https://github.com/ismaan1998/access_dict_by_dot/',
  download_url = 'https://github.com/ismaan1998/access_dict_by_dot/releases/tag/0.0.1',
  keywords=['dictionary', 'dot', 'access'],
  long_description=long_description,
  long_description_content_type='text/markdown',



  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
  ],

)


