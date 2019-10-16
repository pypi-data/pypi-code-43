from json import loads

import click
import os
import sys

from jinja2 import Template


def parse_stdin(file_path):
    with open(file_path, 'r') as f:
        json_input = f.read()
        return loads(json_input)['cluster-ips']['value']


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

    os.makedirs(inventory)
    with open('{}/hosts'.format(inventory), 'w') as f:
        f.write(template.render(master_ip=master_ip, worker_ips=worker_ips))


@click.command()
@click.option('-i', '--inventory-name', 'inventory')
def tool(inventory):
    ips = parse_stdin(sys.stdin.read())
    generate_inventory(ips, inventory)
