from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup(
    name='aws_vpc',
    version='1.0.1',
    packages=find_packages(),
    description=(
        'Infrastructure-as-a-code project which creates a highly opinionated VPC for '
        'troposphere or aws cdk.'
    ),
    long_description=README + '\n\n' + HISTORY,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'boto3',
        'botocore',
        'awscli',
        'aws-cdk.core',
        'aws-cdk.aws-ec2',
        'troposphere'
    ],
    author='Laimonas Sutkus',
    author_email='laimonas.sutkus@gmail.com',
    keywords='AWS SDK CDK Troposphere VPC Infrastructure Cloud',
    url='https://github.com/laimonassutkus/AwsVpc',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
