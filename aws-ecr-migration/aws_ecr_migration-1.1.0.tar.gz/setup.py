from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup(
    name='aws_ecr_migration',
    version='1.1.0',
    packages=find_packages(),
    description=(
        'Management project which migrates docker images to/from ECR repositories.'
    ),
    long_description=README + '\n\n' + HISTORY,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'boto3',
        'botocore',
        'awscli>=1.16.0,<1.17.0'
    ],
    author='Laimonas Sutkus',
    author_email='laimonas@myhealthyapps.com',
    keywords='AWS SDK ECR Docker Container Backup Restore Migration Infrastructure Cloud Lambda',
    url='https://github.com/laimonassutkus/AwsEcrMigration',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux'
    ],
)
