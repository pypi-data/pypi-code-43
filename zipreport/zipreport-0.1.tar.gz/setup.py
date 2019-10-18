from setuptools import setup

from zipreport import __author__, __license__, __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='zipreport',
      version=__version__,
      author=__author__,
      description='Very lightweight PDF report generation',
      long_description_content_type="text/markdown",
      long_description=long_description,
      license=__license__,
      url='https://github.com/iluvcapra/zipreport',
      project_urls={
          'Source':
              'https://github.com/iluvcapra/zipreport',
          'Issues':
              'https://github.com/iluvcapra/zipreport/issues',
      },
      classifiers=[
          'License :: OSI Approved :: MIT License',
          "Programming Language :: Python :: 3.7",
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Topic :: Printing",
          "Topic :: Office/Business"],
      packages=['zipreport'],
      keywords='reports pdf cairo pango',
      install_requires=['pangocffi','cairocffi', 'pangocairocffi']
      )

