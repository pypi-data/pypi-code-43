from setuptools import setup

setup(
    name='henrys_model_utils',    
    version='0.1',
    author='Henry Dashwood',   
    author_email='hcndashwood@gmail.com',
    packages=['henrys_model_utils'],
    install_requires=[
        'torch',
        'fastai'
    ],
)