from setuptools import setup, find_packages
 
setup(name='easierai_common_functions',
      version='1.1.1',
      url='https://gitlab.atosresearch.eu/ari/ioe-ai/common-python-helper-functions',
      license='ATOS',
      author='IoE Lab',
      author_email='juan.carrascoa.external@atos.net',
      description='This library contains reusable code for various projects',
      long_description=open('README.md').read(),
      packages=find_packages(),
      zip_safe=False)
