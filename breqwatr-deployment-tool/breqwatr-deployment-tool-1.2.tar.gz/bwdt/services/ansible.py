""" Controls for the ansible service """
from bwdt.constants import SERVICE_IMAGE_TAGS
from bwdt.lib.container import Docker


def start(ssh_key_path, cloud_yml_path, kolla_dir):
    """ Start the Ansible container """
    name = 'ansible'
    repo = 'breqwatr/ansible'
    tag = SERVICE_IMAGE_TAGS[repo]
    image = '{}:{}'.format(repo, tag)
    docker_kwargs = {
        'volumes':  {
            ssh_key_path: {'bind': '/root/.ssh/id_rsa', 'mode': 'ro'},
            cloud_yml_path: {'bind': '/etc/breqwatr/cloud.yml', 'mode': 'rw'},
            kolla_dir: {'bind': '/etc/kolla', 'mode': 'rw'}
        }
    }
    docker = Docker()
    docker.pull(repository=repo, tag=tag)
    success = docker.run(image, name=name, **docker_kwargs)
    return success


def openstack_genconfig():
    """ Runs the openstack genconfig task """
    cloud_yml = '-e @/etc/breqwatr/cloud.yml'
    conn = '-e ansible_connection=local'
    inv = '-i localhost,'
    playbook = '/var/repos/bw-ansible/generate-kolla-config.yml'
    cmd = 'ansible-playbook {} {} {} {}'.format(cloud_yml, conn, inv, playbook)
    return Docker().execute('ansible', cmd)


def openstack_bootstrap():
    """ Runs kolla-ansible bootstrap """
    cmd = 'kolla-ansible -i /etc/kolla/inventory bootstrap-servers'
    return Docker().execute(container_name='ansible', cmd=cmd)


def openstack_deploy():
    """ Runs kolla-ansible deploy and post-deploy """
    cmd = 'kolla-ansible -i /etc/kolla/inventory deploy'
    return Docker().execute(container_name='ansible', cmd=cmd)


def openstack_postdeploy():
    """ Runs kolla-ansible post-deploy """
    cmd = 'kolla-ansible -i /etc/kolla/inventory post-deploy'
    return Docker().execute(container_name='ansible', cmd=cmd)


def transfer_kolla_dir(server_ip, user='root'):
    """ Transfers the kolla-dir to a remote server """
    mkdir = 'ssh {}@{} "mkdir -p /etc/kolla"'.format(user, server_ip)
    Docker().execute(container_name='ansible', cmd=mkdir)
    scp = 'scp -r /etc/kolla {}@{}:/etc/'.format(user, server_ip)
    Docker().execute(container_name='ansible', cmd=scp)
