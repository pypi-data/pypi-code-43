# -*- coding: utf-8 -*-


from troposphere_mate import Template, cloudformation
from troposphere_mate.orch_example.web_app.config import Config


class MasterTier(Config):
    rel_path = "99-master.json"

    tier1_vpc = None

    def do_create_template(self):
        tpl = Template()
        stack1 = cloudformation.Stack(
            "T1VPC",
            template=tpl,
            TemplateURL="./01-vpc.json",
            Metadata=dict(tag=self.STAGE.get_value()),
        )
        self.template = tpl
        self.tier1_vpc = stack1

        common_tags = dict(
            Name=self.ENVIRONMENT_NAME.get_value(),
            Project=self.PROJECT_NAME_SLUG.get_value(),
            Stage=self.STAGE.get_value(),
            EnvName=self.ENVIRONMENT_NAME.get_value(),
        )
        self.template.metadata = {
            "StackName": self.ENVIRONMENT_NAME.get_value()}
        self.template.update_tags(common_tags, overwrite=False)
