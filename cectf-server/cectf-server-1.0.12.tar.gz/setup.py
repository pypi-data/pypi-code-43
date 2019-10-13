from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cectf-server',
    version='1.0.12',
    author="Daniel Chiquito",
    author_email="daniel.chiquito@gmail.com",
    description='Backend for the CECTF',
    long_description=long_description,
    url="https://github.com/cectf/cectf-server",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-Security',
        'Flask-SQLAlchemy',
        'Flask-Cors',
        'SQLAlchemy',
        'PyMySQL',
        'bcrypt'
    ],
)
