from setuptools import setup, find_packages

def parse_requirements(requirement_file):
    with open(requirement_file) as f:
        return f.readlines()


with open('.\\README.md') as f:
    long_description = f.read()

setup(
    name='swimlane_migrator',
    version='0.4.3',
    packages=find_packages(),
    url='https://swimlane.com',
    license='',
    author='Swimlane',
    author_email='info@swimlane.com',
    description='Swimlane Content Migration Package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=parse_requirements('.\\requirements.txt')
)
