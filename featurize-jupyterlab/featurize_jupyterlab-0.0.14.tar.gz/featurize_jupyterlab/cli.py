import os
import subprocess
import sys
from pathlib import Path
from multiprocessing import Process

import click

PYTHON_INTERPRETER = 'python3'

@click.group()
def cli():
    pass


@cli.command('rpc:server')
def start_rpc_server():
    from .rpc_server import RpcServer
    server = RpcServer(10, "0.0.0.0:6725")
    server.serve()

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
    from .package_manager import package_manager
    package_manager.add_package(package)


@cli.command('package:remove')
@click.argument('package')
def remove_package(package):
    from .package_manager import package_manager
    package_manager.remove_package(package)


@cli.command('package:list')
def list_packages():
    from .package_manager import package_manager
    package_manager.list_packages()


def main():
    cli()

if __name__ == '__main__':
    main()
