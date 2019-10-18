from distutils.core import setup
import setuptools

console_scripts = """
[console_scripts]
sacremoses=farfetcher.cli:cli
"""

setup(
  name = 'farfetcher',
  packages = ['farfetcher'],
  version = '0.0.1',
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
