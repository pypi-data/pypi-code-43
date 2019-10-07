from setuptools import setup, find_packages
from cnvrg.version import VERSION
setup(
    name='cnvrg',
    version=VERSION,
    python_requires='>3.5',
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        'click', 'requests', "boto3", 'colorama', "tqdm", "pyaml", 'tinynetrc', 'pycryptodome', 'psutil', 'dill', 'pytz'
    ],
    author="cnvrg",
    author_email="support@cnvrg.io",
    entry_points='''
        [console_scripts]
        cnvrgp=cnvrg.main:cli
    ''',
)