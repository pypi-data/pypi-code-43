from setuptools import setup

setup(name='kfpubsub',
      version='0.1',
      description='Base redis pubsub implementation',
      url='https://gitlab.com/kas-factory/packages/pubsub',
      author='Antonio @ KF',
      author_email='antonio@kasfactory.net',
      license='MIT',
      packages=['kfpubsub'],
      install_requires=[
          'redis',
      ],
      zip_safe=False)
