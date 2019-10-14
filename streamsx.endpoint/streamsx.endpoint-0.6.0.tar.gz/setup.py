from setuptools import setup
import streamsx.endpoint
setup(
  name = 'streamsx.endpoint',
  packages = ['streamsx.endpoint'],
  include_package_data=True,
  version = streamsx.endpoint.__version__,
  description = 'IBM Streams endpoint integration',
  long_description = open('DESC.txt').read(),
  author = 'IBM Streams @ github.com',
  author_email = 'hegermar@de.ibm.com',
  license='Apache License - Version 2.0',
  url = 'https://github.com/IBMStreams/streamsx.endpoint',
  keywords = ['streams', 'ibmstreams', 'streaming', 'analytics', 'streaming-analytics', 'http', 'endpoint'],
  classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
  install_requires=['streamsx', 'streamsx.toolkits'],
  
  test_suite='nose.collector',
  tests_require=['nose']
)
