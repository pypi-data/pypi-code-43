from setuptools import setup

setup(
    name='sqlite3_api',
    version='1.0.2',
    packages=['sqlite3_api', 'sqlite3_api.test'],
    url='https://github.com/NOnaME-400/sqlite3-api.git',
    license='Apache 2.0',
    author='AlexDev',
    author_email='aleks.filiov@yandex.ru',
    description='API for sqlite3'
)

# twine register dist/sqlite3_api-1.0.1.tar.gz
# twine upload dist/*
