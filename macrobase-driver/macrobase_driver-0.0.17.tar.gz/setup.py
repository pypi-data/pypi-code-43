from setuptools import setup, find_packages

setup(
    name='macrobase_driver',
    version='0.0.17',
    packages=find_packages(),
    url='https://github.com/mbcores/macrobase-driver',
    license='MIT',
    author='Alexey Shagaleev',
    author_email='alexey.shagaleev@yandex.ru',
    description='Macrobase drivers base',
    install_requires=[
        'structlog==19.1.0',
        'python-rapidjson==0.7.0'
    ]
)


