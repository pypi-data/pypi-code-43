# coding=utf-8
import json

from alas_tools.clients.management.configuration import ConfigurationClient
from alas_tools.common.clients.core import normalize_str
from alas_tools.helpers.parnet import get_parnet_config


def get_address_comune(config, addresses_cl, comuna_name, partner=None):
    comuna_name_normalize = normalize_str(comuna_name)

    address_cl = filter(
        lambda x: x['name'] == comuna_name, addresses_cl
    )

    if len(address_cl) == 0:
        address_cl = filter(
            lambda x: normalize_str(x['name']) == comuna_name_normalize, addresses_cl
        )

    if len(address_cl) == 0 and str(comuna_name_normalize)==str('pedro aguirre cerda'):
        address_cl = filter(
            lambda x: normalize_str(x['name']) == 'pedro aguirre cerda', addresses_cl
        )

    if len(address_cl) == 0 and partner is not None:

        partner_config = get_parnet_config(config, partner)

        comune_mapping = filter(
            lambda x: normalize_str(x['key']) == comuna_name_normalize, partner_config['comune_mapping']
        )

        if len(comune_mapping) > 0:
            comuna_name_normalize = normalize_str(comune_mapping[0]['value'])
            address_cl = filter(
                lambda x: normalize_str(x['name']) == comuna_name_normalize, addresses_cl
            )

    return address_cl


def get_addresses(config):
    configuration_client = ConfigurationClient(**config)
    configuration_client.headers['Authorization'] = configuration_client.headers['Authorization'].replace("\n", "")
    return json.loads(configuration_client.get('address-cl.json').content)


def get_address_structure(config, structure_id, addresses_cl=None, addresses_cl_prev=None):
    if not addresses_cl or not addresses_cl_prev:
        addresses_cl = get_addresses(config)

    _address_structure = filter(
        lambda x: int(x['code']) == structure_id,
        addresses_cl
    )

    return _address_structure[0]


def get_address_structure_by_name(config, comuna_name, addresses_cl=None):
    if not addresses_cl:
        addresses_cl, addresses_cl_prev = get_addresses(config)

    comuna_name_normalize = normalize_str(comuna_name)

    _address_structure = filter(
        lambda x: x['name'] == comuna_name, addresses_cl
    )

    if len(_address_structure) == 0:
        _address_structure = filter(
            lambda x: normalize_str(x['name']) == comuna_name_normalize, addresses_cl
        )

    if len(_address_structure) > 0:
        return _address_structure[0]

    return None

