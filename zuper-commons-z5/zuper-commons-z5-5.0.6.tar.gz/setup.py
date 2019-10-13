from setuptools import find_packages, setup


def get_version(filename: str) -> str:
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


version = get_version('src/zuper_commons/__init__.py')
import os

description = """"""


def read(fname: str) -> str:
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


line = 'z5'
setup(name=f'zuper-commons-{line}',
      version=version,
      package_dir={'': 'src'},
      packages=find_packages('src'),

      zip_safe=True,
      entry_points={
          'console_scripts': [],
      },
      install_requires=[
          'dataclasses',
          'xtermcolor',
          'termcolor',
      ],
      )
