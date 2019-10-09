# -*- coding: utf-8 -*-

from troposphere_mate.orch_example.config import Config as BaseConfig
from troposphere_mate import (
    Template, Output, Export, Ref,
    iam
)


class Canned(BaseConfig):
    template = None

    def create_template(self):
        policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListAllMyBuckets",
                        "s3:ListBucket",
                        "s3:HeadBucket"
                    ],
                    "Resource": "*"
                }
            ]
        }

        tpl = Template()
        policy = iam.ManagedPolicy(
            "IamPolicy41",
            template=tpl,
            ManagedPolicyName="{}-policy41".format(
                self.ENVIRONMENT_NAME.get_value()),
            PolicyDocument=policy_doc,
        )
        tpl.add_output(
            Output(
                policy.title,
                Value=Ref(policy),
                Export=Export(
                    "{}-{}".format(self.ENVIRONMENT_NAME.get_value(), policy.title))
            )
        )
        self.template = tpl


if __name__ == "__main__":
    can = Canned(PROJECT_NAME="my_project", STAGE="dev")
    can.create_template()
    can.template.pprint()
