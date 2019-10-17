from json import loads

import click
import os

from jinja2 import Template


def parse_stdin(file_path):
    with open(file_path, 'r') as f:
        json_input = f.read()
        return loads(json_input)['outputs']['cluster-ips']['value']


def generate_inventory(ips, inventory):
    tmpl = """[ds-master]
{{ master_ip }} ansible_user=root ansible_python_interpreter=/usr/bin/python3
[ds-workers]
{% for worker_ip in worker_ips %}{{ worker_ip }} ansible_user=root ansible_python_interpreter=/usr/bin/python3
{% endfor %}
    """
    template = Template(tmpl)
    master_ip = ips[0]
    worker_ips = ips[1:]

    os.makedirs(os.path.abspath(inventory))
    with open('{}/hosts'.format(inventory), 'w') as f:
        f.write(template.render(master_ip=master_ip, worker_ips=worker_ips))


def generate_group_vars(ips, inventory):
    master_tmpl = """ip: {{ master_ip }}
client_ips:
{% for worker_ip in worker_ips %}  - {{ worker_ip }}
{% endfor %}
"""
    workers_tmpl = """
master_ip: {{ master_ip }}    
"""
    dir = os.path.abspath(os.path.join(inventory, 'group_vars'))
    os.makedirs(dir)

    files = {
        os.path.join(dir, 'ds-master'): Template(master_tmpl),
        os.path.join(dir, 'ds-workers'): Template(workers_tmpl)
    }
    master_ip = ips[0]
    worker_ips = ips[1:]

    for filename, tmpl in files.items():
        with open(filename, 'w') as f:
            f.write(tmpl.render(master_ip=master_ip, worker_ips=worker_ips))


@click.command()
@click.option('-i', '--inventory-name', 'inventory')
def tool(inventory):
    ips = parse_stdin('terraform.tfstate')
    generate_inventory(ips, inventory)
    generate_group_vars(ips, inventory)
