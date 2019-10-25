from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call
import os


setup(name='phrase_pickers',
      version='0.2.5',
      description='NLP helpers to parse noun or verb phrases in a sentence using spacy parse tree.',
      url='https://github.com/LocusAnalytics/phrase_pickers',
      author='CAC',
      author_email='cac@locus.co',
      license='Proprietary',
      packages=['phrase_pickers'],
      package_data={
          'phrase_pickers': [
              os.path.join('res', 'morpho_semantic_words.csv.gz'),
              os.path.join('res', 'stopwords.txt.gz'),
              os.path.join('res', 'undesirable_words.json.gz')
          ]
      },
      install_requires=['spacy==2.1.3'],
      zip_safe=False,
      python_requires=">=3.6")

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print('Downloading language model for the spaCy POS tagger\n'
          "(don't worry, this will only happen once)")
    from spacy.cli import download
    download("en_core_web_sm")
