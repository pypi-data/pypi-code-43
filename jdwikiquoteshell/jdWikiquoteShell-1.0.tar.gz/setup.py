#!/usr/bin/env python3

from setuptools import setup

setup(name='jdWikiquoteShell',
      version='1.0',
      description='Prints quotes from wikiquote.org.',
      author='JakobDev',
      author_email='jakobdev@gmx.de',
      url='https://gitlab.com/JakobDev/jdWikiquoteShell',
      include_package_data=True,
      install_requires=[
          'jdTranslationHelper',
          'wikiquote'
      ],
      packages=['jdWikiquoteShell'],
      entry_points={
          'console_scripts': ['jdWikiquoteShell = jdWikiquoteShell.jdWikiquoteShell:main']
          },
      classifiers=["Topic :: Utilities","License :: OSI Approved :: BSD License","Topic :: Internet"],
     )

