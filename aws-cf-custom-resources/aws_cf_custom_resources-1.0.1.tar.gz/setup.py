from setuptools import setup, find_packages

setup(
    name='aws_cf_custom_resources',
    version='1.0.1',
    license='GNU GENERAL PUBLIC LICENSE Version 3',
    packages=find_packages(),
    description='Container library which contains various custom resources for AWS CloudFormation.',
    include_package_data=True,
    install_requires=[
        'boto3',
        'botocore',
        'troposphere',
        'cfnresponse',
        'aws-lambda'
    ],
    author='Laimonas Sutkus',
    author_email='laimonas.sutkus@gmail.com',
    keywords='AWS SDK CloudFormation Infrastructure Cloud CustomResource',
    url='https://github.com/laimonassutkus/AwsCfCustomResources',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],
)
