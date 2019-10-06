""" Controls for the registry service """
from click import echo

from bwdt.constants import KOLLA_IMAGE_TAGS, SERVICE_IMAGE_TAGS
from bwdt.lib.container import Docker


def start(ip='0.0.0.0', port=5000):
    """ Start the registry container """
    name = 'registry'
    repo = 'registry'
    tag = SERVICE_IMAGE_TAGS[repo]
    http_addr = "{}:{}".format(ip, port)
    image = '{}:{}'.format(repo, tag)
    docker_kwargs = {
        'environment': {'REGISTRY_HTTP_ADDR': http_addr},
        'ports': {port: port}
    }
    docker = Docker()
    docker.pull(repository=repo, tag=tag)
    success = docker.run(image, name=name, **docker_kwargs)
    return success


def sync_image(registry_url, image, tag=None):
    """ Pull images from upstream or import from media, push to registry """
    if tag is None:
        tag = KOLLA_IMAGE_TAGS[image]
    docker = Docker()
    docker.pull(image, tag)
    echo('> Applying new tag')
    docker.retag(image, tag, registry_url)
    echo('> Pushing {}:{} to {}'.format(image, tag, registry_url))
    docker.push(image, tag, registry_url)


def sync_all_images(registry_url, tag=None):
    """ Sync all images to registry_url """
    i = 0
    length = len(KOLLA_IMAGE_TAGS)
    for image in KOLLA_IMAGE_TAGS:
        echo('Progress: {} / {}'.format(i, length))
        sync_image(registry_url, image, tag)
        i += 1
