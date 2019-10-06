from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='lgm',
    version='0.0.2',
    description='Lightweight python3 library for natural LanGuage Modeling. Currently, mostly useful for DL/RL experiments with natural language data. Largely based (for now) on the fastai course v3, dl2 (March-April 2019).',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/abrsvn/lgm',
    author='Adrian Brasoveanu',
    author_email='abrsvn@gmail.com',
    license='None',
    packages=['lgm'],
    zip_safe=False
)
