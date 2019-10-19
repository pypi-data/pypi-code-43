from setuptools import setup, find_packages

setup(
    name='pyking',
    version='0.2.0',
    description='富含乱七八糟代码的代码包',
    author='setupdata',
    author_email='ran1144639044@gmail.com',
    url='https://github.com/setupdata/pyking',
    packages=find_packages(),
    install_requires=['requests'],
    include_package_data=True,
)
