#!/usr/bin/env python

from pip.req import parse_requirements
from setuptools import find_packages, setup

requirements = [str(req.req) for req in parse_requirements('requirements.txt', session=False)]

setup(name='cabot_check_influxdb',
      version='0.0.3',
      description='A Influxdb plugin for Cabot',
      author='mlebee',
      author_email='mathieu.lebee@gmail.com',
      url='https://github.com/mlebee/cabot-check-influxdb',
      install_requires=requirements,
      packages=find_packages(),
    )
