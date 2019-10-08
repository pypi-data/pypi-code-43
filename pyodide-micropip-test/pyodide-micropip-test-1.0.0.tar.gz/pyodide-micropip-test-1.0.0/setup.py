from setuptools import setup

def readme():
    with open('README.md') as f:
            return f.read()

setup(
    name = 'pyodide-micropip-test',
    description = 'Test package for package installation in Pyodide',
    long_description = readme(),
    long_description_content_type='text/markdown',
    license = 'MIT',
    version = '1.0.0',

    install_requires = ['snowballstemmer; implementation_name=="cpython"'],

    author = 'Filip Š',
    author_email = 'projects@filips.si',
    url = 'https://github.com/iodide-project/pyodide/pull/528',
    keywords = 'test, test-package, pyodide, micropip',

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],

    include_package_data = True,
)
