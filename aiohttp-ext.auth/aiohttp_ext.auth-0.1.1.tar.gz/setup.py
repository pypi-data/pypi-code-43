"""Пользователи и авторизация"""

from os.path import join, dirname
from setuptools import setup, find_packages


setup(
    name='aiohttp_ext.auth',
    version='0.1.1',
    url='https://bitbucket.org/igor_kovalenko/aiohttp_ext.auth',
    license='BSD',
    author='Kovalenko Igor',
    author_email='kovalenko.s.igor@gmail.com',
    description=__doc__,
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=open(join(dirname(__file__), 'requirements.txt')).readlines(),
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

