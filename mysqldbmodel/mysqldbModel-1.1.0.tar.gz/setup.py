from setuptools import find_packages, setup
setup(
    name='mysqldbModel',  # package
    version='1.1.0',
    description='mongodbModel',
    long_description='args: select、insert、delete、update',
    author='donglidunyin',
    author_email='donglidunyin@163.com',
    install_requires=[
        'PyMySQL>=0.9.3',
        'retrying>=1.3.3',
        'logModel>=0.0.1',
    ],
    packages=find_packages(),
)
