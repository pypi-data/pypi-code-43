from os import path, environ
from os.path import join, abspath, dirname
from setuptools import setup, find_packages

base_path = dirname(abspath(__file__))
requirementPath = join(base_path, 'requirements.txt')
install_requires = []

if path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

test_install_requires = []
testRequirementPath = join(base_path, 'test_requirements.txt')
if path.isfile(testRequirementPath):
    with open(testRequirementPath) as f:
        test_install_requires = f.read().splitlines()

with open(join(base_path, 'README.md'), 'r') as fh:
    long_description = fh.read()

if environ.get('CI_COMMIT_TAG'):
    version = environ['CI_COMMIT_TAG'] # use the tag of the commit if tagged
else:
    version = environ['CI_JOB_ID'] # otherwise use the unique id assigned to the branch

setup(name='nsglib',
      version=version,
      description='NSG Common Python Library',
      author='Richard Kim & Jenifer Cochran',
      author_email='developer.publishers@rgi-corp.com',
      url='https://gitlab.com/GitLabRGI/nsg/nsg-tile-cache/nsg-common-library',
      license='MIT',
      packages=find_packages(include=['nsg',
                                      'nsg.*']),
      tests_require=test_install_requires,
      install_requires=install_requires,
      long_description=long_description,
      long_description_content_type='text/markdown',
      )
