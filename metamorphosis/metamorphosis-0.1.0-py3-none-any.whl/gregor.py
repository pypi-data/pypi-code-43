import click
import importlib

import yaml

from metamorphosis import ConsumerNode

@click.group()
def cli():
    pass

@cli.command()
@click.option('--app', prompt='Module', help='The package and classname')
@click.option('--node-name', prompt="Node Name", help="The name of this node")
@click.option('--limits', prompt='Config YML',
              help='Config yaml with the process limits')
def run_node(node_name, app, limits):
    """Import an app and run the consumers therein"""
    package_name, object_name = app.rsplit('.', 1)
    pkg = importlib.import_module(package_name)
    msvc = getattr(pkg, object_name)
    with open(limits) as limits_stream:
        consumer_limits = yaml.safe_load(limits_stream)

    consumer_node = ConsumerNode(node_name, msvc, consumer_limits)
    consumer_node.start()
    consumer_node.join()


@cli.command()
@click.option('--app', prompt='Module', help='The package and classname')
@click.option('--harakiri-limit', default=None,
              help="Default limit on the number of messages a single consumer can run. Default=None")
@click.option('--harakiri-jitter', default=None,
              help="Default amount by which to vary the harakiri limit up or down")
def default_config(app, harakiri_limit=None, harakiri_jitter=None):
    harakiri_jitter = int(harakiri_jitter) if harakiri_jitter else None
    harakiri_limit = int(harakiri_limit) if harakiri_limit else None
    package_name, object_name = app.rsplit('.', 1)
    pkg = importlib.import_module(package_name)
    msvc = getattr(pkg, object_name)

    print(yaml.dump(msvc.default_consumer_config(harakiri_limit, harakiri_jitter)))

if __name__ == '__main__':
    consumer()