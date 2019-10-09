from setuptools import setup, find_packages

LONG_DESCRIPTION = open("README.md").read()

setup(
    name='peerpkg',
    version='1.8',
    description=LONG_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url='https://github.com/ahmedgirach/peer',
    author='Ahmed Girach',
    author_email='ahmed@peerbits.com',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': ['peerpkg=peerpkg.__init__:main'],
    },
)
