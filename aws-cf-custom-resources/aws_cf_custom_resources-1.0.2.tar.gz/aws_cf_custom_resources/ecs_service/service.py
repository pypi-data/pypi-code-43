import os

from troposphere.iam import Role, Policy
from aws_cf_custom_resources.abstract_custom_service import AbstractCustomService
from aws_cf_custom_resources.ecs_service import ecs_service_root


class EcsServiceService(AbstractCustomService):
    def __init__(self):
        super().__init__()

        self.src = os.path.join(
            ecs_service_root,
            'package'
        )

        self.lambda_handler = 'index.handler'
        self.lambda_runtime = 'python3.6'
        self.lambda_memory = 128
        self.lambda_timeout = 120
        self.lambda_name = 'CfCustomResourceEcsService'
        self.lambda_description = (
            'Lambda function enabling AWS CloudFormation to create ECS Service with newest parameters.'
        )

    def role(self) -> Role:
        return Role(
            "CfCustomResourceEcsServiceLambdaRole",
            Path="/",
            Policies=[Policy(
                PolicyName="CfCustomResourceEcsServiceLambdaPolicy",
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Action": ["logs:*"],
                        "Resource": "arn:aws:logs:*:*:*",
                        "Effect": "Allow"
                    }, {
                        "Action": [
                            "ecs:CreateService",
                            "ecs:UpdateService",
                            "ecs:DeleteService",
                            "iam:PassRole"
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
