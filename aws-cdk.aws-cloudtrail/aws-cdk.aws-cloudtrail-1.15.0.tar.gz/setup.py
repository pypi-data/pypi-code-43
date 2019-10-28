import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-cloudtrail",
    "version": "1.15.0",
    "description": "CDK Constructs for AWS CloudTrail",
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
        "aws_cdk.aws_cloudtrail",
        "aws_cdk.aws_cloudtrail._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_cloudtrail._jsii": [
            "aws-cloudtrail@1.15.0.jsii.tgz"
        ],
        "aws_cdk.aws_cloudtrail": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.19.0",
        "publication>=0.0.3",
        "aws-cdk.aws-events~=1.15,>=1.15.0",
        "aws-cdk.aws-iam~=1.15,>=1.15.0",
        "aws-cdk.aws-kms~=1.15,>=1.15.0",
        "aws-cdk.aws-logs~=1.15,>=1.15.0",
        "aws-cdk.aws-s3~=1.15,>=1.15.0",
        "aws-cdk.core~=1.15,>=1.15.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
