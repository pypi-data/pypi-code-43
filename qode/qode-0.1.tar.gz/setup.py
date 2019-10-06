
from setuptools import setup, find_packages

setup(
    name='qode',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='An example python package',
    long_description=open('README.txt').read(),
    install_requires=['numpy'],
    url='https://github.com/BillMills/python-package-example',
    author='Ismael Benito',
    author_email='ibenito@color-sensing.com'
)
