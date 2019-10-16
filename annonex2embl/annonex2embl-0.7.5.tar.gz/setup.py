import os
import glob
import unittest
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='*_test.py')
    return test_suite

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='annonex2embl',
    version='0.7.5',
    author='Michael Gruenstaeudl, PhD',
    author_email='m.gruenstaeudl@fu-berlin.de',
    description='Converts an annotated DNA multi-sequence alignment (in NEXUS format) to an EMBL flatfile for submission to ENA via the Webin-CLI submission tool',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/michaelgruenstaeudl/annonex2embl',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
        ],
    keywords='novel DNA sequences, public sequence databases, European Nucleotide Archive, file conversion, flatfile',
    license='BSD',
    entry_points={
        'console_scripts': [
            'annonex2embl = annonex2embl.CLIOps:start_annonex2embl'
        ],
    },
    packages=['annonex2embl'], # So that the subfolder 'annonex2embl' is read immediately.
    #packages = find_packages(),
    install_requires=['biopython', 'argparse', 'unidecode'],
    scripts=glob.glob('scripts/*'),
    test_suite='setup.my_test_suite',
    include_package_data=True,
    zip_safe=False
)
