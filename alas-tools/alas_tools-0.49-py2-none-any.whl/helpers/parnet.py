
import json

from alas_tools.clients.management.configuration import ConfigurationClient


def get_parnet_config(config, partner):

    config = json.loads(ConfigurationClient(**config).get('integration-api.json').content)

    partner_config = filter(lambda x: x['partner'] == partner, config)[0]

    if "comune_mapping" not in partner_config:
        partner_config.update({'comune_mapping': {}})

    return partner_config


def get_parnet_config_env(config, partner, env):

    config = json.loads(ConfigurationClient(**config).get('integration-api.json').content)

    partner_config = filter(lambda x: x['partner'] == partner, config)[0]

    if "comune_mapping" not in partner_config:
        partner_config.update({'comune_mapping': {}})

    parnet_config_env = filter(lambda x: x['name'] == env, partner_config["environments"])[0]
    return parnet_config_env
