# -*- coding: utf-8 -*-


from troposphere_mate import Template, cloudformation
from troposphere_mate.orch_example.config import Config as BaseConfig


class Canned(BaseConfig):

    tier1 = None
    tier2 = None
    tier3 = None

    def do_create_template(self):
        tpl = Template()
        stack1 = cloudformation.Stack(
            "T1",
            template=tpl,
            TemplateURL="./01-tier.json",
            Metadata=dict(tag=self.STAGE.get_value()),
        )
        stack2 = cloudformation.Stack(
            "T2",
            template=tpl,
            TemplateURL="./02-tier.json",
            Metadata=dict(tag=self.STAGE.get_value()),
        )
        stack3 = cloudformation.Stack(
            "T3",
            template=tpl,
            TemplateURL="./03-tier.json",
            Metadata=dict(tag=self.STAGE.get_value()),
        )
        self.template = tpl
        self.tier1 = stack1
        self.tier2 = stack2
        self.tier3 = stack3

        common_tags = dict(
            Name=self.ENVIRONMENT_NAME.get_value(),
            Project=self.PROJECT_NAME_SLUG.get_value(),
            Stage=self.STAGE.get_value(),
            EnvName=self.ENVIRONMENT_NAME.get_value(),
        )
        self.template.metadata = {
            "StackName": self.ENVIRONMENT_NAME.get_value()}
        self.template.update_tags(common_tags, overwrite=False)
        return self.template


if __name__ == "__main__":
    can = Canned(PROJECT_NAME="my_project", STAGE="dev")
    can.create_template()
    can.template.pprint()
