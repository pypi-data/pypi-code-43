from cloudcix.client import Client


class IAAS:
    """
    The IAAS application provides services that allow for interaction with infrastructure for purposes such as
    black/whitelisting IP addresses, adding DNS entries, and more.
    """
    _application_name = 'DNS'

    aggregated_blacklist = Client(
        _application_name,
        'AggregatedBlacklist/',
    )
    allocation = Client(
        _application_name,
        'Allocation/',
    )
    asn = Client(
        _application_name,
        'ASN/',
    )
    blacklist = Client(
        _application_name,
        'CIXBlacklist/',
    )
    blacklist_source = Client(
        _application_name,
        'BlacklistSource/',
    )
    cloud = Client(
        _application_name,
        'Cloud/',
    )
    domain = Client(
        _application_name,
        'Domain/',
    )
    hypervisor = Client(
        _application_name,
        'Hypervisor/',
    )
    ike = Client(
        _application_name,
        'IKE/',
    )
    image = Client(
        _application_name,
        'Image/',
    )
    ipaddress = Client(
        _application_name,
        'IPAddress/',
    )
    ipmi = Client(
        _application_name,
        'IPMI/',
    )
    ipsec = Client(
        _application_name,
        'IpSec/',
    )
    ip_validator = Client(
        _application_name,
        'IPValidator/',
    )
    location_hasher = Client(
        _application_name,
        'LocationHasher/',
    )
    macaddress = Client(
        _application_name,
        'Server/{server_id}/MacAddress/',
    )
    nmap = Client(
        _application_name,
        'nmap/',
    )
    pool_ip = Client(
        _application_name,
        'PoolIP/',
    )
    port = Client(
        _application_name,
        'Router/{router_id}/Port/',
    )
    port_config = Client(
        _application_name,
        'Port/{port_id}/PortConfig/',
    )
    port_function = Client(
        _application_name,
        'PortFunction/',
    )
    project = Client(
        _application_name,
        'Project/',
    )
    record = Client(
        _application_name,
        'Record/',
    )
    recordptr = Client(
        _application_name,
        'RecordPTR/',
    )
    router = Client(
        _application_name,
        'Router/',
    )
    router_model = Client(
        _application_name,
        'RouterModel/',
    )
    router_model_port_function = Client(
        _application_name,
        'RouterModelPortFunction/',
    )
    server = Client(
        _application_name,
        'Server/',
    )
    storage = Client(
        _application_name,
        'VM/{vm_id}/Storage/',
    )
    storage_type = Client(
        _application_name,
        'StorageType/',
    )
    subnet = Client(
        _application_name,
        'Subnet/',
    )
    subnet_space = Client(
        _application_name,
        'Allocation/{allocation_id}/Subnet_space/',
    )
    vm = Client(
        _application_name,
        'VM/',
    )
    vm_history = Client(
        _application_name,
        'VM/{vm_id}/VMHistory/',
    )
    vpn_tunnel = Client(
        _application_name,
        'VPNTunnel/',
    )
    vrf = Client(
        _application_name,
        'VRF/',
    )
    whitelist = Client(
        _application_name,
        'CIXWhitelist/',
    )
