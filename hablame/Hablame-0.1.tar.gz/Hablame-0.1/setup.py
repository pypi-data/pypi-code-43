from setuptools import setup, find_packages

setup(name='Hablame',
      version='0.1',
      url='https://drakezair.com',
      license='MIT',
      author='Luis Andrade',
      author_email='andradex.js07@gmail.com',
      description='Add static script_dir() method to Path',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md').read(),
      zip_safe=False)