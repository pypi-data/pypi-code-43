import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.app-delivery",
    "version": "1.15.0",
    "description": "Continuous Integration / Continuous Delivery for CDK Applications",
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
        "aws_cdk.app_delivery",
        "aws_cdk.app_delivery._jsii"
    ],
    "package_data": {
        "aws_cdk.app_delivery._jsii": [
            "app-delivery@1.15.0.jsii.tgz"
        ],
        "aws_cdk.app_delivery": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.19.0",
        "publication>=0.0.3",
        "aws-cdk.aws-cloudformation~=1.15,>=1.15.0",
        "aws-cdk.aws-codebuild~=1.15,>=1.15.0",
        "aws-cdk.aws-codepipeline~=1.15,>=1.15.0",
        "aws-cdk.aws-codepipeline-actions~=1.15,>=1.15.0",
        "aws-cdk.aws-events~=1.15,>=1.15.0",
        "aws-cdk.aws-iam~=1.15,>=1.15.0",
        "aws-cdk.core~=1.15,>=1.15.0",
        "aws-cdk.cx-api~=1.15,>=1.15.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
