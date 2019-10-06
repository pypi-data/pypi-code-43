""" Controls for the ntp service """
from bwdt.constants import SERVICE_IMAGE_TAGS
from bwdt.lib.container import Docker


def start(tag=None):
    """ Start the NTP service """
    name = 'ntp'
    repo = 'breqwatr/ntp'
    tag = SERVICE_IMAGE_TAGS[repo]
    docker = Docker()
    docker.pull(repository=repo, tag=tag)
    image = '{}:{}'.format(repo, tag)
    docker.run(image, name=name, network_mode='host', privileged=True)
