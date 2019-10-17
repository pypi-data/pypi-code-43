from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='PyShareTesting2',
    packages=['PyShare'],
    version='0.6',
    license='MIT',
    description='An example of a python package from pre-existing code',
    include_package_data=True,
)