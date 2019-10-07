#!/usr/bin/env python3

from setuptools import setup

setup(name='jdLangTranslator',
      version='1.3',
      description='A Translator for .lang files.',
      author='JakobDev',
      author_email='jakobdev@gmx.de',
      url='https://gitlab.com/JakobDev/jdLangTranslator',
      include_package_data=True,
      install_requires=[
          'PyQt5',
      ],
      packages=['jdLangTranslator'],
      entry_points={
          'console_scripts': ['jdLangTranslator = jdLangTranslator.jdLangTranslator:main']
          },
      classifiers=["Typing :: Typed"],
     )
