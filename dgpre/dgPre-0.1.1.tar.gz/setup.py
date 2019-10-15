#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages
"""
打包的用的setup必须引入，
"""

VERSION = '0.1.1'

setup(name='dgPre',
      version=VERSION,
      description="a tiny and smart cli player of douyutv,ximalayad,anmu based on Python",
      long_description='just enjoy',
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python douyu danmu danmu.fm terminal',
      author='viton',
      author_email='viton@gmail.com',
      url='https://github.com/viton/doumu.fm',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'requests',
      ],
      entry_points={
        'console_scripts':[
            'sgpre = dgPre.Yuepre:main'
        ]
      },
)
