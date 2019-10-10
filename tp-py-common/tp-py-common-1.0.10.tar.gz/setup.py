from setuptools import setup, find_packages

__version__ = "1.0.10"

entry_points = {}

setup(
    name='tp-py-common',
    scripts=['tp/test/fixtures/load_config.sh', 'tp/test/fixtures/setup.sh'],
    version=__version__,
    description='Common code to be used by various tp packages',
    author='TruePill',
    packages=find_packages(),
    entry_points=entry_points,
)