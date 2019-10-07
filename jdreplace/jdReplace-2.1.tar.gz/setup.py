#!/usr/bin/env python3

from setuptools import setup

setup(name='jdReplace',
      version='2.1',
      description='With jdReplace you can replace a text in all files of a directory.',
      author='JakobDev',
      author_email='jakobdev@gmx.de',
      url='https://gitlab.com/JakobDev/jdReplace',
      include_package_data=True,
      install_requires=[
          'PyQt5',
      ],
      packages=['jdReplace'],
      entry_points={
          'console_scripts': ['jdReplace = jdReplace.jdReplace:main']
          },
     )
