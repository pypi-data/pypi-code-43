from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

with open('README.md') as f:
    long_description = f.read()


def get_version():
    return open('version.txt', 'r').read().strip()


class NumpyBuildExt(build_ext):
    """build_ext command for use when numpy headers are needed."""

    def run(self):
        # Import numpy here, only when headers are needed
        import numpy

        # Add numpy headers to include_dirs
        self.include_dirs.append(numpy.get_include())

        # Call original build_ext command
        build_ext.run(self)


setup(name='dativatools',
      version=get_version(),
      description='A selection of tools for easier processing of data using Pandas and AWS',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://bitbucket.org/dativa4data/dativatools/',
      author='Dativa',
      author_email='hello@dativa.com',
      license='MIT',
      zip_safe=False,
      packages=['dativatools',
                'dativa.tools',
                'dativa.tools.pandas',
                'dativa.tools.aws',
                'dativa.tools.logging',
                'dativa.tools.db'],
      include_package_data=True,
      setup_requires=[
          'setuptools>=41.0.1',
          'wheel>=0.33.4',
          'numpy>=1.13.3'],
      cmdclass={'build_ext': NumpyBuildExt},
      ext_modules=[Extension(name="dativa.tools.pandas.att", sources=["dativa/tools/pandas/att.pyx"])],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Topic :: Software Development :: Libraries',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6'],
      keywords='dativa', )
