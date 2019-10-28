import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-codebuild",
    "version": "1.15.0",
    "description": "CDK Constructs for AWS CodeBuild",
    "url": "https://github.com/aws/aws-cdk",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "project_urls": {
        "Source": "https://github.com/aws/aws-cdk.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_cdk.aws_codebuild",
        "aws_cdk.aws_codebuild._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_codebuild._jsii": [
            "aws-codebuild@1.15.0.jsii.tgz"
        ],
        "aws_cdk.aws_codebuild": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.19.0",
        "publication>=0.0.3",
        "aws-cdk.assets~=1.15,>=1.15.0",
        "aws-cdk.aws-cloudwatch~=1.15,>=1.15.0",
        "aws-cdk.aws-codecommit~=1.15,>=1.15.0",
        "aws-cdk.aws-ec2~=1.15,>=1.15.0",
        "aws-cdk.aws-ecr~=1.15,>=1.15.0",
        "aws-cdk.aws-ecr-assets~=1.15,>=1.15.0",
        "aws-cdk.aws-events~=1.15,>=1.15.0",
        "aws-cdk.aws-iam~=1.15,>=1.15.0",
        "aws-cdk.aws-kms~=1.15,>=1.15.0",
        "aws-cdk.aws-s3~=1.15,>=1.15.0",
        "aws-cdk.aws-s3-assets~=1.15,>=1.15.0",
        "aws-cdk.aws-secretsmanager~=1.15,>=1.15.0",
        "aws-cdk.core~=1.15,>=1.15.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
