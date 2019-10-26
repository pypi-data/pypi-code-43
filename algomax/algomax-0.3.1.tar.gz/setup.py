import setuptools

try:
    from pip._internal.req import parse_requirements
except ImportError:
    from pip.req import parse_requirements


def load_requirements(filename: str):
    requirements = parse_requirements(filename, session='production')
    return [str(requirement.req) for requirement in requirements]


README_PATH = 'README.md'
with open(README_PATH, 'r') as file_reader:
    long_description = file_reader.read()


REQUIREMENTS_PATH = 'requirements.txt'


setuptools.setup(name='algomax',
                 version='0.3.1',
                 author='hadi.f',
                 author_email='h.farhadi@mabnadp.com',
                 entry_points={
                     'console_scripts': [
                        'algomax=algomax.__main__:main'
                     ]
                 },
                 description='cli tool for write your own trade algorithms',
                 long_description=long_description,
                 keywords='algomax EMAX trader cli-trader algomax-cli',
                 long_description_content_type='text/markdown',
                 url='https://mabnadp.com',
                 packages=setuptools.find_packages(),
                 classifiers=[
                    'Programming Language :: Python :: 3',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: OS Independent'
                 ],
                 install_requires=load_requirements(REQUIREMENTS_PATH),
                 python_requires='>=3.6')
