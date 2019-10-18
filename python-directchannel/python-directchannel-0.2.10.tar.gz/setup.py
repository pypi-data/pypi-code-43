from setuptools import setup

setup(name='python-directchannel',
      version='0.2.10',
      description='DirectChannel Mentor API Client',
      url='https://bitbucket.org/metadonors/python-directchannel',
      author='Metadonors',
      author_email='fabrizio.arzeni@metadonors.it',
      license='MIT',
      packages=['pydirectchannel'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)