import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-sns",
    "version": "1.15.0",
    "description": "CDK Constructs for AWS SNS",
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
        "aws_cdk.aws_sns",
        "aws_cdk.aws_sns._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_sns._jsii": [
            "aws-sns@1.15.0.jsii.tgz"
        ],
        "aws_cdk.aws_sns": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.19.0",
        "publication>=0.0.3",
        "aws-cdk.aws-cloudwatch~=1.15,>=1.15.0",
        "aws-cdk.aws-events~=1.15,>=1.15.0",
        "aws-cdk.aws-iam~=1.15,>=1.15.0",
        "aws-cdk.core~=1.15,>=1.15.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
