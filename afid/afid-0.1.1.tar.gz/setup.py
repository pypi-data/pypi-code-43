from setuptools import setup

setup(name='afid',
      version='0.1.1',
      description='Fast affine transformations to incorporate side-information',
      url='http://github.com/rs239/afid',
      author='Rohit Singh',
      author_email='rsingh@alum.mit.edu',
      license='MIT',
      packages=['afid'],
      install_requires = 'numpy,scipy,pandas,sklearn,cvxopt'.split(','),
      zip_safe=False)
