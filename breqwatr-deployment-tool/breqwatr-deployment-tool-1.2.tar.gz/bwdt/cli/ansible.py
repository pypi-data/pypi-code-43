""" Commands for operating the Ansible service """
import click

import bwdt.services.ansible as ansible


@click.group(name='ansible')
def ansible_group():
    """ Command group for bwdt Ansible service """


@click.option('--ssh-key-path', required=True, help='path to SSH private key')
@click.option('--cloud-yml-path', required=True, help='path to cloud.yml file')
@click.option('--kolla-dir', required=True, help='Mount path for kolla files')
@click.command()
def start(ssh_key_path, cloud_yml_path, kolla_dir):
    """Launch the local registry"""
    click.echo("Launching container: breqwatr/ansible")
    success = ansible.start(
        ssh_key_path=ssh_key_path,
        cloud_yml_path=cloud_yml_path,
        kolla_dir=kolla_dir)
    if success:
        click.echo('Done')
    else:
        click.echo('Failed to launch - Maybe its already running?')


@click.option('--server-ip', required=True, help='IP of compute node')
@click.option('--user', required=False, default='root',
              help='Optional username for SSH/SCP. Default: root')
@click.command(name='transfer-kolla-dir')
def transfer_kolla_dir(server_ip, user):
    """ Transfer the Ansible service's kolla dir to a compute node """
    txt = 'Transfering kolla to {}@{}:/etc/kolla'.format(server_ip, user)
    click.echo(txt)
    ansible.transfer_kolla_dir(server_ip, user=user)
    click.echo('Done')


@click.group()
def openstack():
    """ Command group for bwdt ansible openstack """


@click.command(name='gen-config')
def gen_config():
    """ Generate OpenStack config files in the ansible container """
    #click.echo("Generating OpenStack config files")
    #result = ansible.openstack_genconfig()
    #click.echo(result['output'])
    # TODO: Temprary print instead of run until streaming output and socket
    # timeout issues are fixed:
    cloud_yml = '-e @/etc/breqwatr/cloud.yml'
    conn = '-e ansible_connection=local'
    inv = '-i localhost,'
    playbook = '/var/repos/bw-ansible/generate-kolla-config.yml'
    cmd = 'ansible-playbook {} {} {} {}'.format(cloud_yml, conn, inv, playbook)
    docker_cmd = 'docker exec -it ansible {}'.format(cmd)
    click.echo(docker_cmd)


@click.command()
def bootstrap():
    """ Run kolla-ansible bootstrap """
    # click.echo("Running bootstrap task")
    # result = ansible.openstack_bootstrap()
    # click.echo(result['output'])
    # TODO: Temprary print instead of run until streaming output and socket
    # timeout issues are fixed:
    click.echo('docker exec -it ansible kolla-ansible -i /etc/kolla/inventory bootstrap-servers')


@click.command()
def deploy():
    """ Run kolla-ansible deploy """
    # click.echo("Running deploy task")
    # result = ansible.openstack_deploy()
    # click.echo(result['output'])
    # TODO: Temprary print instead of run until streaming output and socket
    # timeout issues are fixed:
    click.echo('docker exec -it ansible kolla-ansible -i /etc/kolla/inventory deploy')


@click.command(name='post-deploy')
def post_deploy():
    """ Run kolla-ansible post-deploy """
    # click.echo("Running post-deploy task")
    # result = ansible.openstack_postdeploy()
    # click.echo(result['output'])
    # TODO: Temprary print instead of run until streaming output and socket
    # timeout issues are fixed:
    click.echo('docker exec -it ansible kolla-ansible -i /etc/kolla/inventory post-deploy')


ansible_group.add_command(transfer_kolla_dir)
ansible_group.add_command(start)

openstack.add_command(gen_config)
openstack.add_command(bootstrap)
openstack.add_command(deploy)
openstack.add_command(post_deploy)
ansible_group.add_command(openstack)
