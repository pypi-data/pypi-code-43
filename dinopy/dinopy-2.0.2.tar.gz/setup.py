# -*- coding: utf-8 -*-
import sys
from functools import partial

import numpy as np
from setuptools import setup, Extension

if "--cythonize" in sys.argv:
    USE_CYTHON = True
    sys.argv.remove("--cythonize")
else:
    USE_CYTHON = False

Extension = partial(Extension, extra_compile_args=["-O3"], include_dirs=[np.get_include()])

# Decide extension type base on cython parameter
ext_c = '.pyx' if USE_CYTHON else '.c'
ext_cpp = '.pyx' if USE_CYTHON else '.cpp'

# Collect all extension modules.
# Use packaged c files if USE_CYTHON is False,
# otherwise build the extensions from the pyx files
# and cythonize them.
c_extensions = [
    Extension(
        "dinopy.{}".format(filename),
        ["dinopy/{}{}".format(filename, ext_c)])
    for filename in
    ["auxiliary", "conversion", "creader", "definitions", "fasta_reader", "fasta_writer", "fastq_reader",
     "fastq_writer", "input_opener", "processors", "shape", "shaping", "output_opener", "nameline_parser", "sam_reader",
     "sam_writer", "sambam"]
]
cpp_extensions = [
    Extension(
        "dinopy.wrap_sais",
        ["dinopy/wrap_sais{}".format(ext_cpp)],
        include_dirs=['dinopy/cpp/'],
        language="c++",
    )]
extensions = c_extensions + cpp_extensions

if USE_CYTHON:
    from Cython.Build import cythonize

    extensions = cythonize(extensions, compiler_directives={
        'language_level': 3,
        'boundscheck': False,
        'nonecheck': False,
        'embedsignature': True,
    })

setup(
    name='dinopy',
    description="DNA input and output library for Python and Cython. Includes reader and writer for FASTA and FASTQ "
                "files, support for samtools faidx files, and generators for solid and gapped q-grams (k-mers).",
    long_description=open("README.rst").read(),
    version='2.0.2',
    author='Henning Timm, Till Hartmann',
    author_email='henning.timm@tu-dortmund.de, till.hartmann@tu-dortmund.de',
    license="MIT",
    url="https://bitbucket.org/HenningTimm/dinopy",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Cython',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],
    packages=['dinopy'],
    # Add cython and c++ files
    package_data={'dinopy': ['*.pyx', '*.pxd', '*.c', '*.cpp', 'cpp/sais.cpp', '../README.rst']},
    install_requires=['numpy>=1.9'],
    extras_require={
        'cython': ['cython>=0.22'],  # This is required for the --cythonize parameter
    },
    ext_modules=extensions,
)
