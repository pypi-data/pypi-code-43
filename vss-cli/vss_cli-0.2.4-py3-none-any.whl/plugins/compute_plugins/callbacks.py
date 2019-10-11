from vss_cli.autocompletion import _init_ctx
from vss_cli.config import Configuration
from vss_cli.helper import to_tuples


def process_networks_opt(ctx: Configuration, param, value):
    _init_ctx(ctx)
    if value is not None:
        networks = list()
        for nic in value:
            _nic = to_tuples(nic)[0]
            _network = _nic[0]
            if len(_nic) > 1:
                _type = ctx.client.get_vm_nic_type_by_name(_nic[1])
                _type = _type[0]['type']
            else:
                _type = 'vmxnet3'
            _net = ctx.client.get_network_by_name_or_moref(_network)
            networks.append({'network': _net[0]['moref'], 'type': _type})
        return networks
