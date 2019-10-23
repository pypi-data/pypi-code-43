"""dbispipeline python packages."""
from setuptools import find_packages, setup

# we should not use the requirements.txt at this point after all.
# https://packaging.python.org/discussions/install-requires-vs-requirements/#requirements-files

setup(
    name="dbispipeline",
    description="should make things more reproducible",
    version="0.1.1",
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
)
