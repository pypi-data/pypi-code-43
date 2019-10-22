from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

packages = find_packages()

setup(
    name='kube_merge',
    version='1.0.1',
    description='kube_merge',
    long_description=readme,
    author='Bogdan Mustiata',
    author_email='bogdan.mustiata@gmail.com',
    license='BSD',
    entry_points={
        "console_scripts": [
            "kube-merge = kube_merge.mainapp:main"
        ]
    },
    install_requires=[
        "click==7.0",
        "PyYaml==5.1.2",
        "colorama",
        "termcolor_util"],
    packages=packages,
    package_data={
        '': ['*.txt', '*.rst']
    })
