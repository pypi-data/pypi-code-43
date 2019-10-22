from distutils.core import setup
import setuptools
import sys
import site
from os import path
from setuptools.command.install import install
import subprocess
import logging

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger()


exec(open('stackd/version.py').read())

setup(
  name='stackd',
  version=__version__,
  description='STACKD - A docker swarm deploy helper according to environment',
  url='https://gitlab.com/youtopia.earth/ops/stackd',
  download_url='https://gitlab.com/youtopia.earth/ops/stackd/-/archive/master/stackd-master.tar.gz',
  keywords = ['docker', 'docker-stack', 'env'],
  author='Idetoile',
  author_email='idetoile@protonmail.com',
  license='MIT',
  packages=setuptools.find_packages(),
  scripts=[
    'stackd/__main__.py',
    'bin/portainer-stack-up',
    'bin/docker-service-logs',
    'bin/docker-stack-volumes-cleanup',
    'bin/docker-stack-rm',
    'bin/completion-stackd.bash',
  ],
  entry_points={
    'console_scripts': [
      'stackd = stackd.__main__:main'
    ]
  },
  install_requires=[
    'PyYAML',
    'wheel',
    'Jinja2'
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
  ],
)
