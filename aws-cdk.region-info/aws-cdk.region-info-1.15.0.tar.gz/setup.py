import json
import setuptools

kwargs = json.loads("""
{
    "name": "aws-cdk.region-info",
    "version": "1.15.0",
    "description": "AWS region information, such as service principal names",
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
        "aws_cdk.region_info",
        "aws_cdk.region_info._jsii"
    ],
    "package_data": {
        "aws_cdk.region_info._jsii": [
            "region-info@1.15.0.jsii.tgz"
        ],
        "aws_cdk.region_info": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "jsii~=0.19.0",
        "publication>=0.0.3"
    ]
}
""")

with open('README.md') as fp:
    kwargs['long_description'] = fp.read()


setuptools.setup(**kwargs)
