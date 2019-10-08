from setuptools import setup, find_packages
import sys


with open('LICENSE', 'r') as f:
  license_content = f.read()

with open('README.md', 'r') as readme_file:
  readme = readme_file.read()

requirements = ['geopy>=1.20.0', 'googlemaps>=3.0', 'numpy>=1.14',
                'pandas>=0.24', 'scipy>=1.1']

extra_requirements = ['GDAL>=2.1.4', 'requests>=2.22',
                      'urllib3>=1.25.6', 'utm>=0.4.2']

setup(name='spatialfriend',
      version='0.0.1',
      author='Aaron Schroeder',
      author_email='aaron@trailzealot.com',
      description='Python library for calculating geospatial data'  \
                + ' from gps coordinates.',
      long_description=readme,
      long_description_content_type='text/markdown',
      url='https://github.com/aaron-schroeder/spatialfriend',
      packages=['spatialfriend'],
      install_requires=requirements,
      extras_require={
        'lidar': ['GDAL>=2.1.4', 'utm>=0.4.2'],
        'natmap': ['requests>=2.22', 'urllib3>=1.25.6'],
      },
      license='MIT License',
      classifiers=['Programming Language :: Python :: 3.6',
                   'License :: OSI Approved :: MIT License',],)
