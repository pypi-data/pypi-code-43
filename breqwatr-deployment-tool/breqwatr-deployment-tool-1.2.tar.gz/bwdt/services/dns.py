""" Controls for the dns service """
from bwdt.constants import SERVICE_IMAGE_TAGS
from bwdt.lib.container import Docker


def start(interface_name, cloud_vip, cloud_fqdn, tag=None):
    """ Start the DNS container """
    name = 'dns'
    repo = 'breqwatr/dns'
    tag = SERVICE_IMAGE_TAGS[repo]
    docker = Docker()
    docker.pull(repository=repo, tag=tag)
    image = '{}:{}'.format(repo, tag)
    env = {
        'INTERFACE': interface_name,
        'CLOUD_VIP': cloud_vip,
        'CLOUD_FQDN': cloud_fqdn,
    }
    docker.run(image, name=name, network_mode='host', environment=env)
