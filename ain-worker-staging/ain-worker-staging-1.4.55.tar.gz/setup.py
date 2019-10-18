from setuptools import setup, find_packages
import os
import dotenv

ENV_PATH = os.path.dirname(os.path.abspath(__file__)) + "/ain/env.development"
ENV = dotenv.dotenv_values(ENV_PATH)

NAME = ENV["NAME"]
VERSION = ENV["VERSION"]

packages = [
  "setuptools",
  "wheel",
  "python-dotenv==0.10.1",
  "docker==3.7.0",
  "requests-unixsocket==0.1.5",
  "requests",
  "click==7.0",
]

setup(
  package_data = {
    '': ['share/*.env', 'share/log/*.env', 'env.development'],
    'share/log': ['*.env'],
    'share': ['*.env'],
  },
  name = NAME,
  version = VERSION,
  python_requires='>=3',
  description = "CLI of " + NAME + " a Python script",
  license = "BSD",
  url = "https://bitbucket.org/comcomai/ain-v1-worker",
  packages=find_packages(),
  install_requires=packages,
  entry_points = {
    'console_scripts' : ['ain = ain.ain:call']
  },
  classifiers=[
    "License :: OSI Approved :: BSD License"
  ]
)
