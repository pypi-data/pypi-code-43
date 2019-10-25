from setuptools import setup
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name = 'narrator',
  packages = ['narrator'],
  version = '0.0.0.2',
  description = 'A set of functions that process and create descriptive summary visualizations to help develop a broader narrative through-line of the tweet data.',
  author = 'Chris A. Lindgren',
  author_email = 'chris.a.lindgren@gmail.com',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url = 'https://github.com/lingeringcode/narrator/',
  download_url = 'https://github.com/lingeringcode/narrator/',
  install_requires = ['pandas', 'numpy', 'emoji', 'nltk', 'matplot'],
  keywords = ['data processing', 'descriptive statistics', 'data narratives', 'temporal charts'],
  classifiers = [],
  include_package_data=True
)
