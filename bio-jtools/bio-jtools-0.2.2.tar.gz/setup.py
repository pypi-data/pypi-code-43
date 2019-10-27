from setuptools import setup, find_packages
from os import path

this_dir = path.abspath(path.dirname(__file__))
with open(path.join(this_dir, 'README.md')) as f:
    long_description = f.read()

# version is defined in jtools/__init__.py
__version__ = 'Undefined'
for line in open(path.join('jtools', '__init__.py')):
    if (line.startswith('__version__')):
        exec(line.strip())

setup(
    name='bio-jtools',
    version=__version__,
    description='Various bioinformatics tools in one package',
    url='http://github.com/jrhawley/bio-jtools',
    author='James Hawley',
    author_email='james.hawley@mail.utoronto.ca',
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English'
    ],
    packages=find_packages(),
    install_requires=[
        'numpy>=1.11',
        'pandas >= 0.15.0',
        'pybedtools',
        'biopython',
        'seaborn',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'jtools=jtools._cli:main'
        ]
    },
    zip_safe=True,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
