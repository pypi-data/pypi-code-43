""" Controls for the Arcus service """
import mysql.connector

from bwdt.constants import SERVICE_IMAGE_TAGS
from bwdt.lib.container import Docker
from bwdt.lib.openstack import Openstack


def _create_arcus_database(cursor):
    """ Create the database named arcus if it doesn't exist """
    cursor.execute("SHOW DATABASES;")
    databases = cursor.fetchall()
    if ('arcus',) in databases:
        return False
    cursor.execute("CREATE DATABASE arcus;")
    return True


def _create_arcus_dbuser(cursor, password):
    """ Create the arcus user in the DB """
    cursor.execute('SELECT user FROM mysql.user;')
    users = cursor.fetchall()
    if (bytearray(b'arcus'),) in users:
        return False
    create_cmd = 'CREATE USER arcus IDENTIFIED BY "{}"'.format(password)
    cursor.execute(create_cmd)
    grant_cmd = 'GRANT ALL privileges ON arcus.* TO "arcus";'
    cursor.execute(grant_cmd)
    return True


def init_database(host, admin_user, admin_passwd, arcus_passwd):
    """ Initialize the Arcus database """
    conn = mysql.connector.connect(host=host, user=admin_user,
                                   passwd=admin_passwd)
    cursor = conn.cursor()
    created_db = _create_arcus_database(cursor)
    created_user = _create_arcus_dbuser(cursor, arcus_passwd)
    return {'created_db': created_db, 'created_user': created_user}


def _create_arcusadmin_openstack_user(openstack, password):
    """ Create the arcusadmin service account in OpenStack """
    users = openstack.keystone.users.list()
    arcus_user = next((usr for usr in users if usr.name == 'arcusadmin'),
                      False)
    if arcus_user:
        return False
    openstack.keystone.users.create(
        name='arcusadmin',
        domain='default',
        password=password,
        email='alerts@breqwatr.com',
        description='Arcus service account')
    return True


def _grant_arcusadmin_openstack_admin_roles(openstack):
    """ Grant amdmin roles to the openstack arcusadmin user """
    user = openstack.keystone.users.find(name='arcusadmin')
    role = openstack.keystone.roles.find(name='admin')
    project = openstack.keystone.projects.find(name='admin')
    openstack.keystone.roles.grant(role=role.id, user=user.id,
                                   project=project.id)
    openstack.keystone.roles.grant(role=role.id, user=user.id,
                                   domain='default')


def create_openstack_sa(fqdn, admin_password, arcus_pass, https=True):
    """ Initialize the OpenStack overcloud for the Arcus service """
    openstack = Openstack(fqdn=fqdn, user='admin', password=admin_password,
                          project='admin', https=https)
    created = _create_arcusadmin_openstack_user(openstack, arcus_pass)
    if created:
        _grant_arcusadmin_openstack_admin_roles(openstack)
    return created


# pylint: disable=R0914
def api_start(fqdn, rabbit_pass, rabbit_ips_list, sql_ip,
              sql_password, ceph_enabled=False, https=True):
    """ Start the Arcus API service """
    name = "arcus_api"
    repo = "breqwatr/arcus-api"
    tag = SERVICE_IMAGE_TAGS[repo]
    image = '{}:{}'.format(repo, tag)
    rabbit_ips_csv = ','.join(rabbit_ips_list)
    docker_kwargs = {
        'environment': {
            'OPENSTACK_VIP': fqdn,
            'PUBLIC_ENDPOINT': 'true',
            'HTTPS_OPENSTACK_APIS': str(https).lower(),
            'RABBITMQ_USERNAME': 'openstack',
            'RABBITMQ_PASSWORD': rabbit_pass,
            'RABBIT_IPS_CSV': rabbit_ips_csv,
            'SQL_USERNAME': 'arcus',
            'SQL_PASSWORD': sql_password,
            'SQL_IP': sql_ip,
            'CEPH_ENABLED': str(ceph_enabled).lower()
        },
        'ports': {'1234': ('0.0.0.0', '1234')},
        'restart_policy': {'Name': 'always'}
    }
    docker = Docker()
    docker.pull(repository=repo, tag=tag)
    success = docker.run(image, name=name, **docker_kwargs)
    return success


def client_start(api_ip, openstack_ip, glance_https=True, arcus_https=False,
                 cert_path=None, cert_key_path=None):
    """ Start the Arcus Client service """
    name = 'arcus_client'
    repo = 'breqwatr/arcus-client'
    tag = SERVICE_IMAGE_TAGS[repo]
    image = '{}:{}'.format(repo, tag)
    docker_kwargs = {
        'environment': {
            'ARCUS_API_IP': api_ip,
            'ARCUS_API_PORT': '1234',
            'OPENSTACK_VIP': openstack_ip,
            'ARCUS_USE_HTTPS': arcus_https,
            'GLANCE_HTTPS': str(glance_https).lower(),
            'VERSION': tag
        },
        'ports': {
            '80': ('0.0.0.0', '80'),
            '443': ('0.0.0.0', '443')
        },
        'restart_policy': {'Name': 'always'}
    }
    if arcus_https:
        docker_kwargs['volumes'] = {
            cert_path: {'bind': '/etc/nginx/haproxy.crt', 'mode': 'ro'},
            cert_key_path: {'bind': '/etc/nginx/haproxy.key', 'mode': 'ro'}}
    docker = Docker()
    docker.pull(repository=repo, tag=tag)
    success = docker.run(image, name=name, **docker_kwargs)
    return success


def mgr_start(openstack_ip, sql_ip, sql_pass, rabbit_ip_list, rabbit_pass,
              kolla_dir, enable_ceph, ssh_key_path):
    """ Start the Arcus Mgr service """
    name = 'arcus_mgr'
    repo = 'breqwatr/arcus-mgr'
    tag = SERVICE_IMAGE_TAGS[repo]
    image = '{}:{}'.format(repo, tag)
    rabbit_ips_csv = ','.join(rabbit_ip_list)
    docker_kwargs = {
        'environment': {
            'OPENSTACK_VIP': openstack_ip,
            'SQL_USERNAME': 'arcus',
            'SQL_PASSWORD': sql_pass,
            'SQL_IP': sql_ip,
            'DR_SQL_USERNAME': 'arcus',
            'DR_SQL_PASSWORD': sql_pass,
            'DR_SQL_IP': sql_ip,
            'RABBIT_NODES_CSV': rabbit_ips_csv,
            'RABBIT_USERNAME': 'openstack',
            'RABBIT_PASSWORD': rabbit_pass,
            'ENABLE_CEPH': str(enable_ceph).lower()
        },
        'volumes': {
            kolla_dir: {'bind': '/etc/kolla/', 'mode': 'rw'},
            ssh_key_path: {'bind': '/root/.ssh/id_rsa', 'mode': 'ro'}
        },
        'restart_policy': {'Name': 'always'},
        'network_mode': 'host'
    }
    docker = Docker()
    docker.pull(repository=repo, tag=tag)
    success = docker.run(image, name=name, **docker_kwargs)
    return success
