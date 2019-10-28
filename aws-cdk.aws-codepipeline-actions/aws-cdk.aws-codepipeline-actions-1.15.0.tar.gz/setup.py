import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.aws-codepipeline-actions",
    "version": "1.15.0",
    "description": "Concrete Actions for AWS Code Pipeline",
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
        "aws_cdk.aws_codepipeline_actions",
        "aws_cdk.aws_codepipeline_actions._jsii"
    ],
    "package_data": {
        "aws_cdk.aws_codepipeline_actions._jsii": [
            "aws-codepipeline-actions@1.15.0.jsii.tgz"
        ],
        "aws_cdk.aws_codepipeline_actions": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.19.0",
        "publication>=0.0.3",
        "aws-cdk.aws-cloudformation~=1.15,>=1.15.0",
        "aws-cdk.aws-codebuild~=1.15,>=1.15.0",
        "aws-cdk.aws-codecommit~=1.15,>=1.15.0",
        "aws-cdk.aws-codedeploy~=1.15,>=1.15.0",
        "aws-cdk.aws-codepipeline~=1.15,>=1.15.0",
        "aws-cdk.aws-ec2~=1.15,>=1.15.0",
        "aws-cdk.aws-ecr~=1.15,>=1.15.0",
        "aws-cdk.aws-ecs~=1.15,>=1.15.0",
        "aws-cdk.aws-events~=1.15,>=1.15.0",
        "aws-cdk.aws-events-targets~=1.15,>=1.15.0",
        "aws-cdk.aws-iam~=1.15,>=1.15.0",
        "aws-cdk.aws-lambda~=1.15,>=1.15.0",
        "aws-cdk.aws-s3~=1.15,>=1.15.0",
        "aws-cdk.aws-sns~=1.15,>=1.15.0",
        "aws-cdk.aws-sns-subscriptions~=1.15,>=1.15.0",
        "aws-cdk.core~=1.15,>=1.15.0"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
