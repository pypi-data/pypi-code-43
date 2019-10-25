"""Install TensorFlow Official Models."""
from setuptools import find_packages
from setuptools import setup

setup(
    name='tf-models-official',
    version='0.0.3.dev0',
    description='TensorFlow Official Models',
    author='Google Inc.',
    author_email='no-reply@google.com',
    url='https://github.com/tensorflow/models',
    license='Apache 2.0',
    packages=find_packages(),
    install_requires=[
        'six',
    ],
    extras_require={
        'tensorflow': ['tensorflow>=2.0.0'],
        'tensorflow_gpu': ['tensorflow-gpu>=2.0.0'],
        'tensorflow-hub': ['tensorflow-hub>=0.6.0'],
    },
)
