import os

from troposphere.iam import Role, Policy
from aws_cf_custom_resources.abstract_custom_service import AbstractCustomService
from aws_cf_custom_resources.cognito_client_secret import cognito_client_secret_root


class CognitoClientSecretService(AbstractCustomService):
    def __init__(self):
        super().__init__()

        self.src = os.path.join(
            cognito_client_secret_root,
            'package'
        )

        self.lambda_handler = 'index.handler'
        self.lambda_runtime = 'python3.6'
        self.lambda_memory = 128
        self.lambda_timeout = 60
        self.lambda_name = 'CfCustomResourceCognitoClientSecret'
        self.lambda_description = (
            'Lambda function enabling AWS CloudFormation '
            'to obtain AWS Cognito user pool client secret.'
        )

    def role(self) -> Role:
        return Role(
            "CfCustomResourceCognitoClientSecretLambdaRole",
            Path="/",
            Policies=[Policy(
                PolicyName="CfCustomResourceCognitoClientSecretLambdaPolicy",
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Action": ["logs:*"],
                        "Resource": "arn:aws:logs:*:*:*",
                        "Effect": "Allow"
                    }, {
                        "Action": ["cognito-idp:DescribeUserPoolClient"],
                        "Resource": "*",
                        "Effect": "Allow"
                    }]
                })],
            AssumeRolePolicyDocument={"Version": "2012-10-17", "Statement": [
                {
                    "Action": ["sts:AssumeRole"],
                    "Effect": "Allow",
                    "Principal": {
                        "Service": [
                            "lambda.amazonaws.com",
                        ]
                    }
                }
            ]},
        )
