from setuptools import setup
import os

__VERSION__="0.0.55"

setup(
    name='micropipes-worker',
    version=__VERSION__,
    description='Micropipes worker package',
    author='Richard Holly',
    author_email='richard.holly@optimaideas.com',
    license='Commercial',
    install_requires=["jsonschema>=3.0.1", "pika>=1.0.0"],
    include_package_data=True,
    packages=['micropipes.shared', 'micropipes.workers'],
    url='https://gitlab.com/aicu/lab/aicu_micropipes',
    zip_safe=False
)