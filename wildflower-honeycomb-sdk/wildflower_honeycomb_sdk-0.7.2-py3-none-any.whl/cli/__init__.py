import os

import boto3
import click

from honeycomb import HoneycombClient

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def get_client(token_uri, audience, client_id, client_secret, url):
    client_credentials = {
        "token_uri": token_uri,
        "audience": audience,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    return HoneycombClient(url, client_credentials=client_credentials)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--token-uri', default=os.getenv('HC_TOKEN_URI', ''), help="Default environment var HC_TOKEN_URI")
@click.option('--audience', default=os.getenv('HC_AUDIENCE', ''), help="Default environment var HC_AUDIENCE")
@click.option('--client-id', default=os.getenv('HC_CLIENT_ID', ''), help="Default environment var HC_CLIENT_ID")
@click.option('--client-secret', default=os.getenv('HC_CLIENT_SECRET', ''), help="Default environment var HC_CLIENT_SECRET")
@click.option('--url', default=os.getenv('HC_URL', ''), help="Default environment var HC_URL")
@click.pass_context
def cli(ctx, token_uri, audience, client_id, client_secret, url):
    """command line interface for the honeycomb sdk."""
    ctx.ensure_object(dict)
    ctx.obj['client'] = get_client(token_uri, audience, client_id, client_secret, url)


@cli.group()
@click.pass_context
def datapoint(ctx):
    """datapoint functions"""


@datapoint.command('get')
@click.argument('data_id')
@click.option('--file-path', help="Save the downloaded file in this path. Default is the current working directory.")
@click.option('--file-name', help="Save the file as this. Default is the last part of the key being downloaded.")
@click.pass_context
def datapoint_get(ctx, data_id, file_path, file_name):
    """get datapoint"""
    query = """query getDP($data_id: ID!) {
        getDatapoint(data_id: $data_id) {
            data_id
            file {key bucketName}}}"""
    variables = {
        "data_id": data_id
    }
    response = ctx.obj['client'].raw_query(query, variables)
    try:
        bucket = response['getDatapoint']['file']['bucketName']
        key = response['getDatapoint']['file']['key']
    except TypeError:
        # raise Exception('Datapoint not found.')
        return click.echo('Datapoint not found.', err=True)

    click.echo('Downloading: {}'.format(os.path.join(bucket, key)))
    if not file_path:
        file_path = os.getcwd()
    if not file_name:
        file_name = '{}-{}'.format(data_id, key.split('/').pop())
    file_ext = key.split('.').pop()
    if not file_name.endswith(file_ext):
        file_name += '.{}'.format(file_ext)
    save_path = os.path.join(file_path, file_name)

    s3 = boto3.resource('s3')
    s3.meta.client.download_file(bucket, key, save_path)
    return click.echo('File saved: {}'.format(save_path))
