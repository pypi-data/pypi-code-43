from setuptools import setup, find_packages

name             = 'giga'
version          = '0.0.1'
author           = 'Nick Zigarovich'
author_email     = 'eckso@eckso.io'
url              = 'https://github.com/ecks0/giga'
description      = 'deploy automation framework'
python_requires  = '>= 3.6'
install_requires = open('requirements.txt').read().strip().splitlines()
packages         = find_packages()
console_scripts  = ['giga=giga.cli:giga']
entry_points     = dict(console_scripts=console_scripts)
zip_safe         = True
long_description = open('README.md').read()
long_description_content_type = 'text/markdown'

setup(
  name=name,
  version=version,
  author=author,
  author_email=author_email,
  url=url,
  description=description,
  python_requires=python_requires,
  install_requires=install_requires,
  packages=packages,
  entry_points=entry_points,
  zip_safe=zip_safe,
  long_description=long_description,
  long_description_content_type=long_description_content_type,
)
