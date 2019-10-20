from setuptools import find_packages, setup

setup(
    name='schemazer',
    version='1.1.18',
    packages=find_packages(exclude=['tests', 'example']),
    author='Dmitriy Danshin',
    author_email='Tingerlink@yandex.ru',
    url='https://gitlab.tingerlink.pro/tingerlink/schemazer',
    include_package_data=True,
    install_requires=[
        'Flask>=0.12.0',
        'werkzeug'
    ]
)
