from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='teampulls',
    version='0.1',
    packages=find_packages(".", exclude=["*.tests", "*.tests.*", "tests.*", "tests", "demo.*"]),
    package_dir = {'':'.'},
    scripts=['src/teampulls'],
    url='https://github.com/brejoc/teampulls',
    license='GPLv3',
    author='Jochen Breuer',
    author_email='jbreuer@suse.de',
    maintainer='Jochen Breuer',
    maintainer_email='jbreuer@suse.de',
    install_requires=requirements,
    description='teampulls lists all of the pull requests for a list of users and repositories and highlights the old ones in red.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='Github Pull Requests team',
    platforms='any',
)
