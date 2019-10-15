#!/usr/bin/env python
from setuptools import setup, find_packages

with open('README.md') as f:
    DESCRIPTION = f.read()


setup(
    name='keras-complex',
    version='0.1.2',
    description='Complex values in Keras - Deep learning for humans',
    license='MIT',
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    url='https://github.com/JesperDramsch/keras-complex',
    packages=find_packages(),
    scripts=['scripts/run.py', 'scripts/training.py'],
    install_requires=[
        "numpy", "scipy", "sklearn", "keras"],
    extras_require={
        "tf": ["tensorflow"],
        "tf_gpu": ["tensorflow-gpu"],
    },
    classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Scientific/Engineering :: Artificial Intelligence',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Documentation :: Sphinx',
          'Natural Language :: English'
      ],
    python_requires='>=3.6',
)
