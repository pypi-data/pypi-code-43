#!/usr/bin/env python3
# NumPy and Cython are required to build from sources
try:
    from Cython.Build import build_ext
except ImportError:  # ModuleNotFoundError is a subclass of ImportError
    raise Exception('Building PyUS from sources requires Cython')
try:
    import numpy as np
except ImportError:  # ModuleNotFoundError is a subclass of ImportError
    raise Exception('Building PyUS from sources requires NumPy')

import os
from setuptools import setup, find_packages, Extension
from distutils.dir_util import copy_tree
from pyus._build_utils.cuda import check_cuda_version
from pyus._build_utils.cython import get_ext_modules
from pyus import __version__

CUDA_VERSION = os.getenv('CUDA_VERSION')
CUDA_VERSION_NB, CUDA_INCLUDE_PATH = check_cuda_version(CUDA_VERSION)


def create_pulse_extension(source):
    """Generate an Extension object from its source file path (.pyx)"""
    # Extract name (remove ext + dotted Python path)
    name = os.path.splitext(source)[0].replace(os.sep, '.')

    # Find relative path from source directory to PULSE library directory
    include_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'pulse', 'include')
    )
    library_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'pyus', 'core', 'lib')
    )
    relpath = os.path.relpath(library_path, os.path.dirname(source))

    # Add $ORIGIN for relative runtime library path
    runpath = os.path.join('$ORIGIN', relpath)

    # TODO(@flomz): check if necessary to link to openmp
    return Extension(
        name=name,
        sources=[source],
        language='c++',
        extra_compile_args=['-std=c++14', '-fopenmp'],
        extra_link_args=['-fopenmp'],
        libraries=['pulse'],
        library_dirs=[library_path],  # path to the lib for the linker
        runtime_library_dirs=[runpath],  # path to find library at run time
        include_dirs=['.',  # adding the '.' to include_dirs is CRUCIAL!!
                      np.get_include(), include_path, CUDA_INCLUDE_PATH],
    )


def main():
    # get pulse extensions
    pulse_extensions = get_ext_modules(
        path='pyus/core/cython',
        create_extension=create_pulse_extension
    )

    setup(
        name='pyus',
        version=__version__,
        description='GPU-accelerated Python package for ultrasound imaging.',
        long_description=open('README.rst').read(),
        author='Dimitris Perdios, Florian Martinez',
        url='https://gitlab.com/pyus/pyus',
        download_url='https://gitlab.com/pyus/pyus/tags',
        # TODO(@flomz): when wheels available
        # python_requires='>=3.5',
        python_requires='>=3.7',
        # can use exclude or specify list [pyus, pyus.probe, ...]
        packages=find_packages(),
        package_data={'pyus.core': ['lib/*.so', 'lib/*.so.*']},  # libpulse.so
        include_package_data=True,
        ext_modules=pulse_extensions,
        # TODO(@dperdios): check if `install_requires` need to be that
        #  restrictive
        install_requires=[
            'numpy>=1.13.3',
            'scipy>=0.19.1',
            # TODO(@dperdios): `scikit-image` when metrics available
            # 'scikit-image>=0.13.1',
            'h5py>=2.8.0',
            'matplotlib>=2.0.2',
            'tqdm>=4.19.1',
            'pyfftw>=0.11.1',
            'pycuda>=2019.1.2'
        ],
        # see pygsp setup.py for more details on extra_require
        # allows to call $ pip install -e pyus[doc,pkg,dev]
        extras_require={
            # 'test': [
            #     'flake8',
            #     'coverage',
            #     'coveralls',
            # ],
            'doc': [
                'Sphinx',
                # 'restview',  # could be useful for online rst viewer
                # 'numpydoc',
                # 'sphinxcontrib-bibtex',
                # 'sphinx-rtd-theme',
            ],
            'pkg': [
                'wheel',
                'twine',
            ],
            'dev': [
                'Cython'
            ],
        },
        # PyPI package information.
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'Environment :: Console',
            'License :: OSI Approved :: BSD License',
            # 'Programming Language :: C++',
            # 'Programming Language :: Python :: 3.5',
            # 'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Operating System :: POSIX :: Linux'
        ],
        license='BSD-3',
        keywords='ultrasound imaging',
        platforms=['Linux'],
        zip_safe=False
    )


if __name__ == '__main__':

    # Copy libs inside pyus package so that they are included in the wheels
    copy_tree('pulse/lib', 'pyus/core/lib')

    main()
