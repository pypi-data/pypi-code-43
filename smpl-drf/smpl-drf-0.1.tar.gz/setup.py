import setuptools
from os.path import join, dirname

import smpl_drf

setuptools.setup(
    name='smpl-drf',
    packages=setuptools.find_packages(),
    version=smpl_drf.__version__,
    license='MIT',
    url='https://github.com/ilya-muhortov/smpl-drf',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown"
)
