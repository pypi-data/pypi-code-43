from setuptools import setup

setup(name='pizdets',
      version='0.16.3',
      description='PMachine Python package',
      url='https://github.com/catalin-rusnac/pizdets',
      author='Catalin Rusnac',
      author_email='crusnac@ist.ac.at',
      license='MIT',
      packages=['pizdets',"pizdets.pm"],
      install_requires=['pandas'],
      zip_safe=True)