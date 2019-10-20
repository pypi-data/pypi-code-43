from setuptools import setup

setup(name='pizdets',
      version='0.16.5',
      description='PMachine Python package',
      url='https://github.com/catalin-rusnac/pizdets',
      author='Catalin Rusnac',
      author_email='crusnac@ist.ac.at',
      license='MIT',
      packages=['pizdets',"pizdets.pm"],
      install_requires=["zmq","google"],
      zip_safe=True)