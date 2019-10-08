# -*- coding: utf-8 -*-

try:
    from typing import List
except:
    pass

from troposphere_mate import ec2
from troposphere_mate import Select, GetAZs, Ref, Tags, Template, Parameter, Output
from troposphere_mate.orch_example.web_app.config import Config


class PrereqTier(Config):
    rel_path = "02-sg.json"

    def do_create_template(self, **kwargs):
        template = Template()

        template.add_parameter(Parameter(Type="string"))
