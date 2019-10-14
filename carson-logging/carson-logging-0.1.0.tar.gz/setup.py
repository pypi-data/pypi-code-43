from distutils.core import setup
from glob import glob
# from setuptools import find_packages
# packages=find_packages(exclude=['contrib', 'docs', 'tests', 'temp'])


with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='carson-logging',
    version='0.1.0',  # x.x.x.{dev, a, b, rc}
    packages=['Carson', r'Carson\Class'],  # to see the detail, please open MANIFEST.in
    license="Apache-2.0",

    author='Carson',
    author_email='jackparadise520a@gmail.com',

    scripts=[],

    install_requires=[],

    url='https://github.com/CarsonSlovoka/carson-logging',
    project_urls={
        'Bug Reports': 'https://github.com/CarsonSlovoka/carson-logging/issues',
        # 'Funding': '',
        # 'Say Thanks!': '',
        # 'Source': '',
    },

    description='easier to use original python provides a module of logging',
    long_description=long_description,
    long_description_content_type='text/x-rst',  # text/markdown  # https://packaging.python.org/guides/making-a-pypi-friendly-readme/
    keywords=['logging', 'log'],

    download_url='https://github.com/CarsonSlovoka/carson-logging/tarball/v0.1.0',
    python_requires='>=3.6.2, <4',

    zip_safe=False,
    classifiers=[  # https://pypi.org/classifiers/
        'Topic :: System :: Logging',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: English',
        'Operating System :: Microsoft',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
