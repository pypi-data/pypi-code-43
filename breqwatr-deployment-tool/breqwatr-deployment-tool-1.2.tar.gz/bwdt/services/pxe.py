""" Controls for the PXE service """
from bwdt.constants import SERVICE_IMAGE_TAGS
from bwdt.lib.container import Docker


def start(interface, dhcp_start, dhcp_end, dns_ip='8.8.8.8'):
    """ Start the breqwatr-pxe container """
    name = 'pxe'
    repo = "breqwatr/pxe"
    tag = SERVICE_IMAGE_TAGS[repo]
    image = '{}:{}'.format(repo, tag)
    docker_kwargs = {
        'privileged': True,
        'network_mode': 'host',
        'environment': {
            'INTERFACE': interface,
            'DHCP_RANGE_START': dhcp_start,
            'DHCP_RANGE_END': dhcp_end,
            'DNS_IP': dns_ip
        },
        'sysctls': {'net.ipv4.ip_forward': 1}
    }
    docker = Docker()
    docker.pull(repository=repo, tag=tag)
    success = docker.run(image, name=name, **docker_kwargs)
    return success
