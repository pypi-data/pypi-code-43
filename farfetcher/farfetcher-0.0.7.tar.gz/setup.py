from distutils.core import setup
import setuptools

console_scripts = """
[console_scripts]
farfetcher=farfetcher.cli:cli
"""

setup(
  name = 'farfetcher',
  packages = ['farfetcher'],
  version = '0.0.7',
  description = '',
  long_description = '',
  author = '',
  license = 'MIT',
  url = 'https://github.com/alvations/farfetcher',
  keywords = [],
  classifiers = [],
  install_requires = ['pandas', 'requests', 'click', 'tqdm'],
  entry_points=console_scripts,
)
