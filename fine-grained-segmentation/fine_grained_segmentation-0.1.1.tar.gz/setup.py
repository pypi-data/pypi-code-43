"""
The build/compilations setup

>> pip install -r requirements.txt
>> python setup.py install
"""
import pip
import logging
import pkg_resources
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
    
try:
    from pip._internal import download
except ImportError:
    from pip import download


def _parse_requirements(file_path):
    pip_ver = pkg_resources.get_distribution('pip').version
    pip_version = list(map(int, pip_ver.split('.')[:2]))
    if pip_version >= [6, 0]:
        raw = parse_requirements(file_path,
                                         session=download.PipSession())
    else:
        raw = parse_requirements(file_path)
    return [str(i.req) for i in raw]


# parse_requirements() returns generator of pip.req.InstallRequirement objects
try:
    install_reqs = _parse_requirements("requirements.txt")
except Exception:
    logging.warning('Fail load requirements file, so using default ones.')
    install_reqs = []

setup(
    name='fine_grained_segmentation',
    version='0.1.1',
    url='https://github.com/vinny-palumbo/fine_grained_segmentation',
    author='Vincent Palumbo',
    author_email='vinnypalumbo.com@gmail.com',
    license='MIT',
    description='Mask R-CNN for Fine-Grained segmentation',
    packages=["fine_grained_segmentation"],
    install_requires=install_reqs,
    include_package_data=True,
    python_requires='>=3.4',
    long_description=open('README.md').read(),
)
