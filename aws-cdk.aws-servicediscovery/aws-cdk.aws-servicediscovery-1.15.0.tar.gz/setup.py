import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-servicediscovery",
    "version": "1.15.0",
    "description": "The CDK Construct Library for AWS::ServiceDiscovery",
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
        "aws_cdk.aws_servicediscovery",
        "aws_cdk.aws_servicediscovery._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_servicediscovery._jsii": [
            "aws-servicediscovery@1.15.0.jsii.tgz"
        ],
        "aws_cdk.aws_servicediscovery": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.19.0",
        "publication>=0.0.3",
        "aws-cdk.aws-ec2~=1.15,>=1.15.0",
        "aws-cdk.aws-elasticloadbalancingv2~=1.15,>=1.15.0",
        "aws-cdk.aws-route53~=1.15,>=1.15.0",
        "aws-cdk.core~=1.15,>=1.15.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
