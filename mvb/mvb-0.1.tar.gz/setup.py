from setuptools import setup, find_packages

setup(
  name='mvb',
  version='0.1',
  author='Michael Van Beek',
  author_email='michaelsvanbeek@gmail.com',
  packages=[
    'mvb',
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Topic :: Utilities'
  ],
  install_requires=['pandas']
)
