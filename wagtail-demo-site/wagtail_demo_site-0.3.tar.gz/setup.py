import os
from setuptools import setup, find_packages


setup(

  name = 'wagtail_demo_site',
  packages=find_packages(),
  version = 0.3,
  license='MIT',
  description = 'web wagtail site',
  author = 'Alexandro.by',
  author_email = 'alexander.ermak@celadon.ae',
  install_requires=[
    'psycopg2-binary==2.8.2',
    'uWSGI==2.0.18',
    'wagtail==2.6.1',
    'django-cors-headers==3.0.2',
    'Django>=2.2,<2.3',
    'wagtail>=2.6,<2.7'
      ],
  include_package_data=True,
 # scripts=['manage.py',],



)



