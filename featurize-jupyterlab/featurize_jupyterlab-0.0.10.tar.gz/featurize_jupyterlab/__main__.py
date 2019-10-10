import os
import subprocess
import sys
from pathlib import Path
from multiprocessing import Process

import append_sys_path  # noqa: F401
import click

PYTHON_INTERPRETER = 'python3'


def start_rpc_server():
    from .rpc import RpcServer
    server = RpcServer(10, f"{os.getenv('BIND_IP_ADDR')}:{os.getenv('RPC_SERVER_PORT')}")
    server.serve()


def start_socket_server():
    process = subprocess.Popen(
        ['gunicorn', '-b', f"{os.getenv('BIND_IP_ADDR')}:{os.getenv('WEB_SOCKET_PORT')}", '--worker-class', 'eventlet', 'wsgi_apps:pusher'],
        cwd=Path(__file__).parent,
        stdout=sys.stdout
    )
    process.wait()


@click.group()
def cli():
    pass


@cli.command('proto:compile')
def proto_compile():
    minetorch_dir = Path(__file__).resolve().parents[1]
    proto_dir = Path('featurize_jupyterlab') / 'proto'
    subprocess.Popen([
        PYTHON_INTERPRETER,
        "-m",
        "grpc_tools.protoc",
        f"-I.",
        f"--python_out=.",
        f"--grpc_python_out=.",
        f"{proto_dir / 'minetorch.proto'}"
    ], stdout=sys.stdout, cwd=minetorch_dir)


@cli.command('runtime:run')
@click.option('--config', help='Absolute path of the config file', required=True)
def runtime_run(config):
    from run import main
    main(config)


@cli.command('package:add')
@click.argument('package')
def add_package(package):
    from package_manager import package_manager
    package_manager.add_package(package)


@cli.command('package:remove')
@click.argument('package')
def remove_package(package):
    from package_manager import package_manager
    package_manager.remove_package(package)


@cli.command('package:list')
def list_packages():
    from package_manager import package_manager
    package_manager.list_packages()


if __name__ == '__main__':
    cli()
