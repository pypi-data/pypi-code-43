from distutils.core import setup
from setuptools import setup, find_packages

setup(
  name = 'taskmonk-sdk',
  packages = ['taskmonk', 'taskmonk.utils'],
  version = '0.17',
  license='apache-2.0',
  description = 'SDK for accessing TaskMonk functionality',
  author = 'Taskmonk',
  author_email = 'info@taskmonk.com',
  url = 'https://github.com/taskmonk/taskmonk-sdk-python',
  download_url = 'https://github.com/taskmonk/taskmonk-sdk-python/archive/v_0.10.tar.gz',
  keywords = ['TaskMonk', 'SDK'],
  install_requires=[
  	'requests'
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
