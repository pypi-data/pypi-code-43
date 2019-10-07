import os

from troposphere.iam import Role, Policy
from aws_cf_custom_resources.abstract_custom_service import AbstractCustomService
from aws_cf_custom_resources.git_commit import git_commit_root


class GitCommitService(AbstractCustomService):
    def __init__(self):
        super().__init__()

        self.src = os.path.join(
            git_commit_root,
            'package'
        )

        self.lambda_handler = 'index.handler'
        self.lambda_runtime = 'python3.6'
        self.lambda_memory = 128
        self.lambda_timeout = 120
        self.lambda_name = 'CfCustomResourceGitCommit'
        self.lambda_description = (
            'Lambda function enabling AWS CloudFormation to create commits to git repositories.'
        )

    def role(self) -> Role:
        return Role(
            "CfCustomResourceGitCommitLambdaRole",
            Path="/",
            Policies=[Policy(
                PolicyName="CfCustomResourceGitCommitLambdaPolicy",
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Action": ["logs:*"],
                        "Resource": "arn:aws:logs:*:*:*",
                        "Effect": "Allow"
                    }, {
                        "Action": [
                            "codecommit:CreateCommit",
                            "codecommit:GetBranch",
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
