from setuptools import setup
from setuptools import find_packages
from codecs import open

with open('README', encoding='utf-8') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ita',
    version='0.1.1',
    description='support package for "introduction to algorithm" lecture',
    long_description=readme,
    author='Akimasa Morihata',
    author_email='morihata@graco.c.u-tokyo.ac.jp',
    url='https://lecture.ecc.u-tokyo.ac.jp/johzu/joho-kagaku/',
    license=license,
    install_requires=['numpy', 'matplotlib' ],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent" ]
)
