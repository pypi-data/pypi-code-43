from setuptools import setup

setup(name='djangopubsub',
      version='0.1.1',
      description='Base redis pubsub django wrapper',
      url='https://gitlab.com/kas-factory/packages/django-pubsub',
      author='Antonio @ KF',
      author_email='antonio@kasfactory.net',
      license='MIT',
      packages=['djangopubsub'],
      package_data={'djangopubsub': ['djangopubsub/*',
                                     'djangopubsub/management/*',
                                     'djangopubsub/management/commands/*']},
      install_requires=[
            'Django',
            'kfpubsub'
      ],
      zip_safe=False
)
