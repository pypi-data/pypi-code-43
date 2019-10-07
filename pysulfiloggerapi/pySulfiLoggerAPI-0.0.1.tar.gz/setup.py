from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pySulfiLoggerAPI',
      version='0.0.1',
      description='Driver module for the SulfiLogger sensor',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://sulfilogger.com',
      author='Unisense',
      author_email='sulfilogger@unisense.com',
      license='',
      packages=['pySulfiLoggerAPI'],
      install_requires=[
          'pyserial',
      ],
      classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: PyPy"
      ],
      zip_safe=False)