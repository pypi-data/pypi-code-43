# python setup.py sdist bdist_wheel
# twine check dist/*
# twine upload --repository pypi dist/*
# twine upload --skip-existing dist/*

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Theos-python-functions",
    version="0.0.6.0",
    author="Theo van der Sluijs",
    author_email="theo@vandersluijs.nl",
    description="Some nice to have python functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tvdsluijs/Theos-Python-Functions",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
