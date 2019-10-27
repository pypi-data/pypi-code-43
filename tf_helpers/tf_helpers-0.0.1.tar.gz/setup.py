# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='tf_helpers',
    version='0.0.1',
    author='Larissa Triess',
    author_email='mail@triess.eu',
    description='A collection of useful functions for TensorFlow for training and visualization.',
    url='https://github.com/ltriess/tf_helpers',
    license='MIT',
    packages=find_packages(exclude=['docs', 'tests']),
    python_requires='>=3.5',
    install_requires=[
        'numpy',
        'matplotlib',
    ],
    extras_require={
        'tf': ['tensorflow'],
        'tf_gpu': ['tensorflow-gpu'],
    },
)
