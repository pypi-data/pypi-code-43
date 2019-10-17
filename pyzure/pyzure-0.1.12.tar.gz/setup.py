from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

setup(
    name='pyzure',
    version='0.1.12',
    description='Easily send data to Microsoft Azure SQL DB',
    long_description=readme,
    author='Dacker',
    author_email='hello@dacker.co',
    url='https://github.com/dacker-team/pyzure',
    keywords='send data microsoft azure sql db easy',
    packages=find_packages(exclude=('tests', 'docs')),
    package_data={'': ["requirements.txt"]},
    python_requires='>=3',
    install_requires=[
        "pyodbc>=4.0.17",
        "pandas>=0.25.0",
        "dbstream>=0.0.10",
        "emoji>=0.5.4"
    ],
)
