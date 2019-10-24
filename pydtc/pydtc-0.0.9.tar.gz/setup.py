from setuptools import find_packages, setup

## create folder for user to store the jdbc driver jars
import os
jdbc_driver = os.path.join(os.path.expanduser('~'), 'jdbc_driver')
if not os.path.exists(jdbc_driver):
    os.makedirs(jdbc_driver)

project_name = 'pydtc'
## read version from __init__.py
import re
version = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format('__version__'), 
                   open(project_name + '/__init__.py').read()).group(1)

setup(
  name = project_name,
  packages = ['pydtc'],
  version = version, 
  description = 'tools collection for data engineer',
  long_description = open('README.md').read(),
  long_description_content_type = "text/markdown",  
  author = 'cctester',
  author_email = 'cctester2001@gmail.com',
  url = 'https://github.com/cctester/pydtc',
  keywords = ['pandas', 'multiprocessing', 'database', 'restapi', 'requests'],
  python_requires = ">=3.5",
  install_requires = [
          'pandas',
          'JayDeBeApi',
          'JPype1 == 0.6.3',
          'asyncio',
          'aiohttp'
      ],
  classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
  ],
)
