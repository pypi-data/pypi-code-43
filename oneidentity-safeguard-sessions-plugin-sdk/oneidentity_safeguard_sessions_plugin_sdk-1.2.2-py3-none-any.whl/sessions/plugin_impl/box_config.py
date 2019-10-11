#
# Copyright (c) 2006-2019 Balabit
# All Rights Reserved.
#

from safeguard.sessions.plugin.box_configuration_settings import extract_http_proxy_settings


stable_box_configuration = {
    'gateway_fqdn': None,
    'starling_join_credential_string': None,
    'http_proxy': None,
}
unstable_box_configuration = {}


class BoxConfig:
    @classmethod
    def query(cls, end_point):
        keys = [item for item in end_point.split('/') if item]
        return cls._get_value(unstable_box_configuration, keys)

    @classmethod
    def _get_value(cls, model, keys):
        try:
            return cls._get_value(model[keys[0]], keys[1:]) if keys else model
        except KeyError:
            return {
                'error':
                {
                    'details': {'mount_point': '/', 'resource': keys[0]},
                    'message': 'Resource was not found', 'type': 'ResourceNotFound'
                 }
            }

    @classmethod
    def get_gateway_fqdn(cls):
        return stable_box_configuration['gateway_fqdn']

    @classmethod
    def get_starling_join_credential_string(cls):
        return stable_box_configuration['starling_join_credential_string']

    @classmethod
    def get_http_proxy(cls):
        response_body = stable_box_configuration['http_proxy']
        return extract_http_proxy_settings(response_body)
