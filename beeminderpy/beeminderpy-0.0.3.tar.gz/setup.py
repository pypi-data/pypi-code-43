import codecs
from setuptools import setup, find_packages
import os
import re


with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'beeminderpy', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


install_requires = ['aiohttp>=3.0']


setup(name='beeminderpy',
      version=version,
      description="Python async wrapper for the Beeminder REST API",
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: AsyncIO',
      ],
      author='Lukasz Jachym',
      author_email='lukasz.jachym@gmail.com',
      url='https://github.com/b1r3k/beeminderpy/',
      license='MIT',
      packages=find_packages(),
      python_requires='>=3.6',
      install_requires=install_requires,
      entry_points={
          'console_scripts': [
              'beeminderpy = beeminderpy.cli:main',
          ]
      },
      include_package_data=True)
