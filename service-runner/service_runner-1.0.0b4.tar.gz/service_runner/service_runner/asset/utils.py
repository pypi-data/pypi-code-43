from service_runner.service_runner.answeb.ansible_api import AnsibleApi
from service_runner.service_runner.asset.models import Host
from django.conf import settings

DEFAULT_PLAYBOOKS_PATH = settings.BASE_DIR + '/service_runner/answeb/playbooks/'


def format_uptime_result(host, result):
    callback = {
        'message': '',
        'data': {}
    }
    if result.get('success'):
        host.status = 1
        data = result.get('success').get(host.ip)
        callback['message'] = 'success'
        callback['data']['uptime'] = data.get('stdout')
        callback['data']['status'] = host.get_status_display()
    elif result.get('failed'):
        host.status = 2
        callback['message'] = 'failed'
        callback['data']['uptime'] = result.get('failed').get(host.ip)
        callback['data']['status'] = host.get_status_display()
    elif result.get('unreachable'):
        host.status = 2
        callback['message'] = 'unreachable'
        callback['data']['uptime'] = result.get('unreachable').get(host.ip)
        callback['data']['status'] = host.get_status_display()
    host.save()
    return callback


def format_result(host, result):
    callback = {}
    if result.get('success'):
        data = result.get('success').get(host.ip)
        callback['message'] = 'success'
        callback['data'] = data.get('out.stdout_lines')
    elif result.get('failed'):
        callback['message'] = 'failed'
        callback['data'] = result.get('failed').get(host.ip)
    elif result.get('unreachable'):
        callback['message'] = 'unreachable'
        callback['data'] = result.get('unreachable').get(host.ip)
    return callback


def get_host_uptime(host_id):
    callback = {}
    host = Host.objects.get(id=host_id)
    api = AnsibleApi(host.ip + ',')
    if host.ssh_key:
        api.options = api.create_options(remote_user=host.ssh_user,
                                         private_key_file=host.ssh_key.ssh_key.path)
    else:
        api.options = api.create_options(remote_user=host.ssh_user)
        api.passwords = dict(sshpass=host.ssh_passwd)

    api.initializeData()
    api.run(host.ip, 'shell', 'uptime')
    result = api.get_result()
    callback = format_uptime_result(host, result)

    return callback


def get_host_info(host_id):
    host = Host.objects.get(id=host_id)
    api = AnsibleApi(host.ip + ',')
    if host.ssh_key:
        api.options = api.create_options(remote_user=host.ssh_user,
                                         private_key_file=host.ssh_key.ssh_key.path)
    else:
        api.options = api.create_options(remote_user=host.ssh_user)
        api.passwords = dict(sshpass=host.ssh_passwd)

    api.initializeData()
    # api.run(host.ip, 'shell', 'uptime')
    api.run_playbook(host.ip,
                     [DEFAULT_PLAYBOOKS_PATH + 'memory_cpu_diskspace_uptime.yml'])
    callback = format_result(host, api.get_result())
    return callback
