import os

from troposphere.iam import Role, Policy
from aws_cf_custom_resources.abstract_custom_service import AbstractCustomService
from aws_cf_custom_resources.deployment_group import deployment_group_root


class DeploymentGroupService(AbstractCustomService):
    def __init__(self):
        super().__init__()

        self.src = os.path.join(
            deployment_group_root,
            'package'
        )

        self.lambda_handler = 'index.handler'
        self.lambda_runtime = 'python3.6'
        self.lambda_memory = 128
        self.lambda_timeout = 120
        self.lambda_name = 'CfCustomResourceDeploymentGroup'
        self.lambda_description = (
            'Lambda function enabling AWS CloudFormation to create a deployment group with newest parameters.'
        )

    def role(self) -> Role:
        return Role(
            "CfCustomResourceDeploymentGroupLambdaRole",
            Path="/",
            Policies=[Policy(
                PolicyName="CfCustomResourceDeploymentGroupLambdaPolicy",
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Action": ["logs:*"],
                        "Resource": "arn:aws:logs:*:*:*",
                        "Effect": "Allow"
                    }, {
                        "Action": [
                            "codedeploy:CreateDeploymentGroup",
                            "codedeploy:UpdateDeploymentGroup",
                            "codedeploy:DeleteDeploymentGroup",
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
