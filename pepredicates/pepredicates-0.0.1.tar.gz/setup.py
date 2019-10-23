from setuptools import setup

version = "0.0.1"


def full_description():
    """Get the full readme
    """
    with open("README.md", "r") as f:
        readme = f.read()
    return readme


def write_version_file(version):
    """Add the version number and the git hash to the file
    'pepredicates.__init__.py'

    Parameters
    ----------
    version: str
        the release version of the code that you are running
    """
    with open("pepredicates/.version", "w") as f:
        f.writelines([version])
    return ".version"


version_file = write_version_file(version)
readme = full_description()

setup(name='pepredicates',
      version=version,
      description=('Python package to return source classification '
                   'probabilities for GW posterior samples'),
      author='Will Farr, Chris Pankow, Charlie Hoy',
      author_email='will.far@ligo.org',
      url='https://git.ligo.org/will.farr/pepredicates',
      download_url='https://git.ligo.org/will.farr/pepredicates',
      install_requires=[
          "astropy",
          "numpy",
          "matplotlib",
          "seaborn"],
      include_package_data=True,
      packages=['pepredicates'],
      package_data={
          'pepredicates': [version_file],
      },
      classifiers=[
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6"],
      license='GNU',
      long_description=readme,
      long_description_content_type='text/markdown')
