from setuptools import find_packages, setup

setup(
    name='mateusz_hello_application',
    version='1.0.0',
    packages=find_packages(),
    include_package_data= True,
    package_dir={'':'.'},
    description='Application Hello by Mateusz'
)