import os

from troposphere.iam import Role, Policy
from aws_cf_custom_resources.abstract_custom_service import AbstractCustomService
from aws_cf_custom_resources.cognito_domain import cognito_domain_root


class CognitoDomainService(AbstractCustomService):
    def __init__(self):
        super().__init__()

        self.src = os.path.join(
            cognito_domain_root,
            'package'
        )

        self.lambda_handler = 'index.handler'
        self.lambda_runtime = 'python3.6'
        self.lambda_memory = 128
        self.lambda_timeout = 60
        self.lambda_name = 'CfCustomResourceCognitoUserPoolDomainName'
        self.lambda_description = (
            'Lambda function enabling AWS CloudFormation '
            'to create domain name for AWS Cognito user pool.'
        )

    def role(self) -> Role:
        return Role(
            "CfCustomResourceCognitoUserPoolDomainNameLambdaRole",
            Path="/",
            Policies=[Policy(
                PolicyName="CfCustomResourceCognitoUserPoolDomainNameLambdaPolicy",
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Action": ["logs:*"],
                        "Resource": "arn:aws:logs:*:*:*",
                        "Effect": "Allow"
                    }, {
                        "Action": [
                            "cognito-idp:CreateUserPoolDomain",
                            "cognito-idp:UpdateUserPoolDomain",
                            "cognito-idp:DeleteUserPoolDomain",
                        ],
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
