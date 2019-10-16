from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

packages = find_packages()

setup(
    name='arst',
    version='1.1.0',
    description='Poor man\'s yo generator.',
    long_description=readme,
    author='Bogdan Mustiata',
    author_email='bogdan.mustiata@gmail.com',
    license='BSD',
    entry_points={
        "console_scripts": [
            "ars = arst.mainapp:main",
            "arst = arst.mainapp:main"
        ]
    },
    install_requires=[
        "pybars3 >=0.9.3, < 0.10",
        "termcolor_util >=1.0.1, < 1.1",
        "colorama >=0.3.7, <0.4",
        "mdvl >=2017.7.16.7, <2017.8",
        "PyYAML >=5.1, <5.2",
        "click==7.0",
        ""],
    packages=packages,
    package_data={
        '': ['*.txt', '*.rst']
    }
)
