#!/usr/bin/python3
from distutils.core import setup


setup(
  name = 'vmxparser',
  py_modules = ['vmxparser'],
  version = '0.1.1',
  license='MIT',
  description = 'Parse a VMX (VMWare) file into a python dict',
  author = 'sphipu',
  author_email = 'sphipu@gmx.ch',
  url = 'https://gitlab.com/sphipu/vmxparser',
  keywords = ['VMX', 'VMWARE'],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Topic :: System :: Systems Administration',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)