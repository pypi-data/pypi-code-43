"""
Sanic-JWT-Extended
"""
import io
import re
import os
from setuptools import setup


with open("README.md", "r") as f:
    long_description = f.read()


with open(os.path.join("entry_logger_sanic", "__init__.py"), "r") as f:
    try:
        version = re.findall(
            r"^__version__ = \"([^']+)\"\r?$", f.read(), re.M
        )[0]
    except IndexError:
        raise RuntimeError("Unable to determine version.")


setup(name='entry-logger-sanic',
      version=version,
      url='https://github.com/EntryDSM/entry-logger-sanic',
      license='MIT',
      author='NovemberOscar',
      author_email='kim@seonghyeon.dev',
      description='NDJSON formatted logger integration with Sanic',
      long_description=long_description,
      long_description_content_type="text/markdown",
      keywords=['sanic', 'log', 'logger'],
      packages=['entry_logger_sanic'],
      zip_safe=False,
      platforms='any',
      install_requires=[
          'Sanic',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ])