from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='django-vegetarian-cookbook',
    version='1.0.9',
    packages=find_packages(exclude=['example']),
    author='Sergey Panasenko',
    author_email='sergey.panasenko@gmail.com',
    description='Django application for the publication of vegetarian culinary recipes with the calculation of energy and nutrients.',
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    zip_safe=False,
    license='AGPL v3',
    install_requires=requirements,
    url='https://github.com/sergey-panasenko/django-vegetarian-cookbook',
)
