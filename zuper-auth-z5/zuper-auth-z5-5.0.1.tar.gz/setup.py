from setuptools import setup, find_packages


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version

line = 'z5'
version = get_version('src/zuper_auth/__init__.py')
import os

description = """"""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name=f'zuper-auth-{line}',
      version=version,
      package_dir={'': 'src'},
      packages=find_packages('src'),

      zip_safe=True,
      entry_points={
          'console_scripts': [

          ]
      },
      install_requires=[

      ],
      )
