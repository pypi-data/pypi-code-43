#!/usr/bin/env python

import os
import re
import sys
from setuptools import find_packages, setup

# marker for basic and basic libs in requirements.txt
BASIC_LIB_MARKER = '#basic-lib'

install_requires = []
dependency_links = []
extra_requires = []

# root code folder
THIS_FOLDER = os.path.realpath(os.path.dirname(__file__))


# determine version
with open(os.path.join(THIS_FOLDER, 'localstack_ext', 'constants.py')) as f:
    configs = f.read()
version = re.search(r'^\s*VERSION\s*=\s*[\'"](.+)[\'"]\s*$', configs, re.MULTILINE).group(1)

# read requirements
with open(os.path.join(THIS_FOLDER, 'requirements.txt')) as f:
    requirements = f.read()

for line in re.split('\n', requirements):
    if line and line[0] == '#' and '#egg=' in line:
        line = re.search(r'#\s*(.*)', line).group(1)
    if line and line[0] != '#':
        if '://' not in line:
            lib_stripped = line.split(' #')[0].strip()
            if BASIC_LIB_MARKER in line:
                install_requires.append(lib_stripped)
            else:
                extra_requires.append(lib_stripped)


if sys.version_info[:2] < (3, 4):
    # remove libs that require Python 3+
    install_requires = [d for d in install_requires if 'hbmqtt' not in d]
    extra_requires = [d for d in extra_requires if 'hbmqtt' not in d]


package_data = {
    '': ['*.md'],
    'localstack_ext': [
        'utils/*.py.enc',
        'utils/aws/*.py.enc',
        'services/*.py.enc',
        'services/apigateway/*.py.enc',
        'services/athena/*.py.enc',
        'services/awslambda/*.py.enc',
        'services/cloudformation/*.py.enc',
        'services/cloudfront/*.py.enc',
        'services/cognito/*.py.enc',
        'services/ec2/*.py.enc',
        'services/ecs/*.py.enc',
        'services/eks/*.py.enc',
        'services/elasticache/*.py.enc',
        'services/glue/*.py.enc',
        'services/iam/*.py.enc',
        'services/iot/*.py.enc',
        'services/kms/*.py.enc',
        'services/rds/*.py.enc',
        'services/sqs/*.py.enc',
        'services/sts/*.py.enc',
        'services/xray/*.py.enc'
    ]}


if __name__ == '__main__':

    setup(
        name='localstack-ext',
        version=version,
        description='Extensions for LocalStack',
        author='Waldemar Hummer',
        author_email='waldemar.hummer@gmail.com',
        url='https://github.com/localstack/localstack',
        packages=find_packages(exclude=('tests', 'tests.*')),
        package_data=package_data,
        install_requires=install_requires,
        dependency_links=dependency_links,
        extras_require={
            'full': extra_requires
        },
        test_suite='tests',
        zip_safe=False,
        classifiers=[
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'License :: OSI Approved :: Apache Software License',
            'Topic :: Software Development :: Testing',
        ]
    )
