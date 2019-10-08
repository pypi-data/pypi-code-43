# -*- coding: utf-8 -*-

from os.path import join
from troposphere_mate import Template, iam, policies
from troposphere_mate.orch_example.web_app.config import Config
from troposphere_mate.canned.iam import (
    AWSServiceName,
    AWSManagedPolicyArn,
    create_assume_role_policy_document,
)


class MicroServiceMasterTier(Config):
    rel_path = join("app1-micro-service", "99-master.json")

    tier1_vpc = None

    def do_create_template(self):
        tpl = Template()
        self.template = tpl
        # iam.Role(
        #     title="",
        #     template=tpl,
        #     AssumeRolePolicyDocument=create_assume_role_policy_document([AWSServiceName.aws_Lambda,]),
        #     RoleName="{}-lambda-execution".format(self.ENVIRONMENT_NAME.get_value()),
        #     ManagedPolicyArns="",
        # )
        # stack1 = cloudformation.Stack(
        #     "T1VPC",
        #     template=tpl,
        #     TemplateURL="./01-vpc.json",
        #     Metadata=dict(tag=self.STAGE.get_value()),
        # )
        # self.template = tpl
        # self.tier1_vpc = stack1
        #
        # common_tags = dict(
        #     Name=self.ENVIRONMENT_NAME.get_value(),
        #     Project=self.PROJECT_NAME_SLUG.get_value(),
        #     Stage=self.STAGE.get_value(),
        #     EnvName=self.ENVIRONMENT_NAME.get_value(),
        # )
        # self.template.metadata = {"StackName": self.ENVIRONMENT_NAME.get_value()}
        # self.template.update_tags(common_tags, overwrite=False)

        return self.template


if __name__ == "__main__":
    tier = MicroServiceMasterTier(PROJECT_NAME="myproject", STAGE="dev")
    tier.create_template()
    tier.template.pprint()
