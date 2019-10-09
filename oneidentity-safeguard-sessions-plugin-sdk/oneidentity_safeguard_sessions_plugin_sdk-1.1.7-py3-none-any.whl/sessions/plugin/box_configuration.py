#
# Copyright (c) 2006-2019 Balabit
# All Rights Reserved.
#
"""
.. py:module:: safeguard.sessions.plugin.box_configuration
    :synopsis: Provide access to SPS configuration model.
"""
from safeguard.sessions.plugin_impl.box_config import BoxConfig


class BoxConfiguration:
    def __init__(self, box_config):
        self.box_config = box_config

    @classmethod
    def open(cls):
        return cls(BoxConfig())

    def _query(self, end_point):
        return self.box_config.query(end_point)

    def get_gateway_fqdn(self):
        return self.box_config.get_gateway_fqdn()

    def get_starling_join_credential_string(self):
        return self.box_config.get_starling_join_credential_string()
