"""
Setup Module to setup Python Handlers (Git Handlers) for the Git Plugin.
"""
import setuptools
import os

readme_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')
with open(readme_file, 'r') as fh:
    long_description = fh.read()

requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
with open(requirements_file, 'r') as f:
    required = f.read().splitlines()

setuptools.setup(
    name='featurize_jupyterlab',
    version='0.0.14',
    author='',
    description="A server extension for JupyterLab's featurize extension",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=required,
    include_package_data=True,
        entry_points = {
        'console_scripts': ['featurize_server=featurize_jupyterlab:cli'],
    }
)
