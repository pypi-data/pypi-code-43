"""dbispipeline python packages."""
from setuptools import find_packages, setup

# we should not use the requirements.txt at this point after all.
# https://packaging.python.org/discussions/install-requires-vs-requirements/#requirements-files

with open('README.md') as fh:
    long_description = fh.read()

setup(
    name="dbispipeline",
    version="0.1.2",
    author="Benjamin Murauer",
    author_email="b.murauer@posteo.de",
    description="should make things more reproducible",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://git.uibk.ac.at/dbis/software/dbispipeline',

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'gitpython>2',
        'sqlalchemy>1.3',
        'scikit-learn',
        'pandas',
        'psycopg2-binary',
        'matplotlib',
    ],
    python_requires='>=3.6',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
    ]
)
