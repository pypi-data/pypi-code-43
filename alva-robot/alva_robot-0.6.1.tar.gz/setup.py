# coding=utf8

__author__ = 'Alexander.Li'

from setuptools import setup, find_packages

version = '0.6.1'

setup(name='alva_robot',
      version=version,
      description="A robot base of AlvaIM",
      long_description="""\
Recieve and process messages and make response for robot of AlvaIM""",
      classifiers=[],
      keywords='AlvaIM, Robot',
      author='Alexander.Li',
      author_email='superpowerlee@gmail.com',
      url='https://alvaim.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'pollworker',
          'secp256k1py',
          'boto3',
          'click',
          'oss2'
      ],
      entry_points={
        'console_scripts': ['alva-robot=alva_robot.main:main'],
      },
      )
