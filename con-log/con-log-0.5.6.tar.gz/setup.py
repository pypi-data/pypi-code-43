from io import open

from setuptools import find_packages, setup

with open('conlog/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

readme_file="README.md"
readme = ""

with open(readme_file, 'r', encoding='utf-8') as f:
    readme = f.read()

REQUIRES = ['wrapt', 'colored']

setup(
    name='con-log',
    version=version,
    description='',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Czwirl Coldwind',
    author_email='czwirl@gmail.com',
    maintainer='Czwirl Coldwind',
    maintainer_email='czwirl@gmail.com',
    url='https://github.com/czwirl/conlog',
    license='MIT',
    
    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],

    package_dir={'conlog': 'conlog'},
    packages=find_packages()
)
