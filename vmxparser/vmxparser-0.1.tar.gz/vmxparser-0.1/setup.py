#!/usr/bin/python3
from distutils.core import setup


setup(
  name = 'vmxparser',         # How you named your package folder (MyLib)
  modules = ['vmxparser'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Parse a VMX (VMWare) file into a python dict',   # Give a short description about your library
  author = 'sphipu',                   # Type in your name
  author_email = 'sphipu@gmx.ch',      # Type in your E-Mail
  url = 'https://gitlab.com/sphipu/vmxparser',   # Provide either the link to your github or to your website
  keywords = ['VMX', 'VMWARE'],   # Keywords that define your package best
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: System :: Systems Administration',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)