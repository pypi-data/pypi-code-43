import os
import click
from tabulate import tabulate
from demyst.common.config import load_config

@click.group()
def channel():
    pass

@channel.command()
@click.option('--config_file', default=None, required=False, help='Config file or ./demyst.config')
@click.option('--username', default=None, required=False, help='Username.')
@click.option('--password', default=None, required=False, help='Password.')
@click.option('--key', default=None, required=False, help='API key.')
@click.option('--env', default="prod", required=False, help='Environment (stg or prod).')
@click.option('--region', default="us", required=False, help='Region.')
def list(config_file, username, password, key, env, region):
    config = load_config(config_file=config_file, username=username, password=password, key=key, env=env, region=region)
    """List all channels belonging to org."""

    url = config.get('MANTA_URL') + 'channels'
    resp = config.auth_get(url)

    channels = resp.json()
    table = []
    headers = ['ID', 'Name', 'Region', 'Pipes', 'Data Functions', 'Protected']

    for channel in channels:
        dfs = [pipe['data_function_name'] for pipe in channel['pipes']]
        num_dfs = sum(df is not None for df in dfs)
        channels[0]['pipes'][0]['data_function_name']
        table.append([channel['id'], channel['name'], channel['region'], len(channel['pipes']), num_dfs, channel['protected']])
    click.echo(tabulate(table, headers, tablefmt="presto"))
