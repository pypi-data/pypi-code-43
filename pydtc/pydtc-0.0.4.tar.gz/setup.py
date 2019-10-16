from setuptools import find_packages, setup

import os
## create folder for user to store the jdbc driver jars
jdbc_driver = os.path.join(os.path.expanduser('~'), 'jdbc_driver')
if not os.path.exists(jdbc_driver):
    os.makedirs(jdbc_driver)

## load project long description
with open("README.md", "r") as f:
    long_description = f.read()

setup(
  name = 'pydtc',
  packages = ['pydtc'],
  version = '0.0.4', 
  description = 'data engineer tools collection',
  long_description=long_description,
  long_description_content_type="text/markdown",  
  author = 'cctester',
  author_email = 'cctester2001@gmail.com',
  url = 'https://github.com/cctester/pydtc',
  keywords = ['pandas', 'multiprocessing', 'database'],
  install_requires=[
          'pandas',
          'JayDeBeApi',
          'JPype1 == 0.6.3',
          'asyncio'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
  ],
)
