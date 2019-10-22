"""
Publishing:
    either:
        $make publish
    or manually:
        run tests
        remember to change the version in setup(... ) below
        $ git commit -am "<my message>"
        $ git push
        $ git tag -a v<my.version.id> -m "<comment to my version>"  # tag version
        $ git push origin v<my.version.id>  # explicitly push tag to the shared server
        $ python setup.py sdist
        $ twine upload dist/*

"""
from setuptools import setup, find_packages
import os
title = os.path.basename(os.path.abspath('.'))
exec(open("./{title}/__about__.py".format(**locals())).read())

with open(os.path.join('.', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=title,
    version=__version__,
    description=__summary__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=__author__,
    author_email=__email__,
    license=__license__,
    keywords=__keywords__,
    packages=find_packages(),
    url=__uri__,
    project_urls={
        'Documentation': __uri__,
        'Source': __uri__,
    },
    test_require=[
        'doctest',
        'unittest',
        'nose',
    ],
    install_requires=__dependencies__,
    classifiers=__classifiers__,
    python_requires=__python_requires__,
)


# in the terminal:
# pip install .
