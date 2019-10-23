try: 
    from setuptools.core import setup
except ImportError as e:
    from distutils.core import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='my-nlp',
    version='0.12',
    description='my nlp toolkit',
    author='Xiaolong Liang',
    author_email='rembern@126.com',
    url='https://github.com/unhappydog/mynlp.git',
    packages=['mynlp', 'mynlp.preprocess', 'mynlp.features', 'mynlp.utils'],
    package_data={'mynlp': ['data/*.dat']},
    install_requires=['numpy', 'nltk', 'sklearn', 'gensim'],
    test_suite='tests',
    long_description=long_description,
    long_description_content_type='text/markdown', 
)
