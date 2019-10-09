# -*- coding: utf-8 -*-

from troposphere_mate import MultiEnvBasicConfig, Constant, Derivable


class Config(MultiEnvBasicConfig):
    AWS_PROFILE = Constant()
    TIER_TAG = Derivable()

    @TIER_TAG.getter
    def get_tier_tag(self):
        return self.STAGE.get_value()

    TIER_LIST_TO_DEPLOY = Constant()
