import os
from setuptools import setup
import pyabf

# load the descripntion
PATH_HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.abspath(PATH_HERE+"/README.rst")) as f:
    long_description = f.read()
    print("loaded description: (%s lines)"%(long_description.count("\n")))

# standard pypi stuff
setup(
    name='pyabf',
    version=pyabf.__version__,
    author='Scott W Harden',
    author_email='SWHarden@gmail.com',
    packages=['pyabf', 'pyabf.tools'],
    url='http://github.com/swharden/pyABF',
    license='MIT License',
    platforms='any',
    description='Python library for reading files in Axon Binary Format (ABF)',
    long_description=long_description,
    install_requires=[
        'matplotlib>=2.1.0',
        'numpy>=1.13.3',
    ],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)
