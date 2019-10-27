from setuptools import find_packages, setup

setup(
    name='project_bm',
    version='4.2.0',
    author='Bartosz Munzel',
    author_email='df.bartoszmunzel@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    package_dir={'': '.'},
    description='Projekt z zajec'
)