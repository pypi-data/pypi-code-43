from setuptools import setup, find_packages
 
setup(name='Interclip',
      version='0.1',
      url='https://github.com/aperta-principium/Interclip/',
      license='MIT',
      author='Filip Troníček',
      author_email='filip.tronicek@seznam.cz',
      description='Interclip API functionality',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md').read(),
      zip_safe=False)