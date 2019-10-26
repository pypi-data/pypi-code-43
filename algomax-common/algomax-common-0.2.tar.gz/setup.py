from setuptools import setup, find_packages


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


REQUIREMENT_PATH = 'requirements.txt'

setup(name='algomax-common',
      version='0.2',
      author='hadi.f',
      author_email='h.farhadi@mabnadp.com',
      description='a common package for algomax-cli and algomax-engine',
      long_description=long_description,
      keywords='algomax-common',
      long_description_content_type='text/markdown',
      url='https://mabnadp.com',
      packages=find_packages(),
      classifiers=[
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent'
      ],
      install_requires=load_requirements(REQUIREMENT_PATH),
      python_requires='>=3.6'
      )