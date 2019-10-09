import boto3
import click


def iter_keys(client):
    keys = client.list_access_keys()
    for key in keys['AccessKeyMetadata']:
        yield key

    marker = keys.get('Marker')
    while marker:
        keys = client.list_access_keys(Marker=marker)
        marker = keys.get('Marker')
        for key in keys['AccessKeyMetadata']:
            yield key


def validate_aws_vars(ctx, param, value):
    if value:
        return value
    raise click.BadParameter('cannot be blank.')


def user_name(ctx):
    user = ctx.obj.get('user_name')
    if user:
        return user
    for key in iter_keys(ctx.obj['client']):
        user = key['UserName']
        ctx.obj['user_name'] = user
        return user


@click.group()
@click.option('--access_key', help='AWS_ACCESS_KEY_ID to use', prompt='Access Key', envvar='AWS_ACCESS_KEY_ID', callback=validate_aws_vars)
@click.option('--secret_key', help=' AWS_SECRET_ACCESS_KEY to use', prompt='Secret Key', envvar='AWS_SECRET_ACCESS_KEY', callback=validate_aws_vars)
@click.pass_context
def cli(ctx, access_key, secret_key):
    ctx.ensure_object(dict)
    opts = {}
    if access_key:
        opts['aws_access_key_id'] = access_key
    if secret_key:
        opts['aws_secret_access_key'] = secret_key
    client = boto3.client('iam', **opts)
    ctx.obj['client'] = client


@cli.command()
@click.pass_context
def list(ctx):
    for key in iter_keys(ctx.obj['client']):
        print(key)


@cli.command()
@click.pass_context
def create(ctx):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.create_access_key
    client = ctx.obj['client']
    user = user_name(ctx)
    response = client.create_access_key(UserName=user)
    print(response)


@cli.command()
@click.pass_context
@click.argument('access_key')
def activate(ctx, access_key):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.update_access_key
    client = ctx.obj['client']
    user = user_name(ctx)
    response = client.update_access_key(
        UserName=user,
        AccessKeyId=access_key,
        Status='Active',
    )
    print(response)


@cli.command()
@click.pass_context
@click.argument('access_key')
def deactivate(ctx, access_key):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.update_access_key
    client = ctx.obj['client']
    user = user_name(ctx)
    response = client.update_access_key(
        UserName=user,
        AccessKeyId=access_key,
        Status='Inactive',
    )
    print(response)


@cli.command()
@click.pass_context
@click.argument('access_key')
def delete(ctx, access_key):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.delete_access_key
    client = ctx.obj['client']
    user = user_name(ctx)
    response = client.delete_access_key(
        UserName=user,
        AccessKeyId=access_key,
    )
    print(response)
