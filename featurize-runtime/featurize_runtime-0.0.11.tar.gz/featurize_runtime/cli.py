import click
import sys
import subprocess
from pathlib import Path

@click.group()
def cli():
    pass

@cli.command('proto:compile')
def proto_compile():
    proto_dir = Path('featurize_runtime')
    subprocess.Popen([
        "python3",
        "-m",
        "grpc_tools.protoc",
        f"-I.",
        f"--python_out=.",
        f"--grpc_python_out=.",
        f"{'minetorch.proto'}"
    ], stdout=sys.stdout, cwd=proto_dir)

@cli.command('run')
@click.option('--config', help='Absolute path of the config file', required=True)
def runtime_run(config):
    from .run import main_process
    main_process(config)

if __name__ == '__main__':
    cli()
