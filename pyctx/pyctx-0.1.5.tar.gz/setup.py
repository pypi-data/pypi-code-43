import os

from setuptools import setup

__ROOT_DIR__ = os.path.abspath(os.path.dirname(__file__))


def readme():
    with open(os.path.join(__ROOT_DIR__, 'README.md')) as f:
        return f.read()


def get_info():
    info = {}
    with open(os.path.join(__ROOT_DIR__, 'pyctx', '__version__.py'), 'r') as f:
        exec(f.read(), info)
    return info


package_info = get_info()

setup(name=package_info['__title__'],
      version=package_info['__version__'],
      description=package_info['__description__'],
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.7',
      ],
      keywords='funniest joke comedy flying circus',
      url=package_info['__url__'],
      author=package_info['__author__'],
      author_email=package_info['__author_email__'],
      license=package_info['__license__'],
      packages=['pyctx'],
      install_requires=[

      ],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      )
