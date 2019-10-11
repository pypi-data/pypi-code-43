# -*- coding: utf-8 -*-
# setup.py
from setuptools import find_packages, setup
from va import __version__



with open('README.rst') as f:
    long_description = f.read()

setup(
    name="va",
    # version="0.0.0.dev5",
    version=__version__,
    packages=find_packages(),
    exclude_package_data={
        'va':['test/*', 'va/onedepva.py'],
    },
    include_package_data=True,
    author="Zhe Wang",
    author_email="zhe@ebi.ac.uk",
    description="CryoEM validation toolkit",
    long_description=long_description,
    long_description_content_type='text/x-rst; charset=UTF-8',
    url="https://test.pypi.org/project/va/",
    license="Apache License",
    keywords="EMDB,Cryoem, Validation",
    # setup_requires=[
    #     "setuptools",
    #     "wheel",
    #     "twine",
    # ],
    install_requires=[
        "numpy",
        "scipy>=0.14",
        "scikit-learn",
        "requests",
        "weave",
        "Pillow",
        "memory-profiler",
        "matplotlib",
        "pandas",
        "weave",
        "mrcfile",
        "biopython>=1.73",
    ],
    classifiers=[
        # maturity
        'Development Status :: 2 - Pre-Alpha',
        # environment
        'Environment :: Console',
        # audience
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        # license
        'License :: OSI Approved :: Apache Software License',
        # python version
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        'console_scripts': [
            'va = va.mainva:main',
        ]
    },
)
