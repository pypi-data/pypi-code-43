# -*- coding: utf-8 -*-
import click
import re
import yaml

from spell.cli.exceptions import api_client_exception_handler, ExitException
from spell.cli.utils import HiddenOption, tabulate_rows, convert_to_local_time
from spell.cli.utils import with_emoji


@click.group(name="model-servers", short_help="Manage model servers",
             help="""Manage model servers

             With no subcommand, displays all of your model servers""",
             invoke_without_command=True)
@click.option("--raw", help="display output in raw format", is_flag=True, default=False,
              cls=HiddenOption)
@click.pass_context
def model_servers(ctx, raw):
    if not ctx.invoked_subcommand:
        client = ctx.obj["client"]
        with api_client_exception_handler():
            model_servers = client.get_model_servers()
        if len(model_servers) == 0:
            click.echo("There are no model servers to display.")
        else:
            data = [(ms.get_specifier(), ms.url, ms.status, ms.get_age()) for ms in model_servers]
            tabulate_rows(data,
                          headers=["NAME", "URL", "STATUS", "AGE"],
                          raw=raw)


@model_servers.command(name="create", short_help="Create a new model server",
                       help="""Create a new Tensorflow model server with the specified NAME from
                       resources stored at PATH. NAME should be fully qualified, following the
                       format: <model_name>:<tag>""")
@click.pass_context
@click.argument("name")
@click.argument("path")
@click.option("--type", "-t", type=click.Choice(["tensorflow", "pytorch"]),
              help="""Please see the documentation located at https://spell.run/docs/model_servers
                   to correctly structure your model for the various supported types.""")
@click.option("--cluster-name", type=str, help="Name of the cluster where the model server will be created")
def create(ctx, name, path, type, cluster_name):
    server_name, tag = get_name_and_tag(name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        model_server = client.new_model_server(server_name=server_name,
                                               tag=tag,
                                               path=path,
                                               type=type,
                                               cluster_name=cluster_name)
    click.echo("Successfully created model server: {}".format(model_server.get_specifier()))


@model_servers.command(name="rm", short_help="Remove a model server",
                       help="""Remove the model server with the specified NAME""")
@click.pass_context
@click.argument("name")
def remove(ctx, name):
    server_name, tag = get_name_and_tag(name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        client.delete_model_server(server_name=server_name, tag=tag)
    click.echo("Successfully removed model server {}".format(name))


@model_servers.command(name="start", short_help="Start a model server",
                       help="""Start the model server with the specified NAME""")
@click.pass_context
@click.argument("name")
def start(ctx, name):
    server_name, tag = get_name_and_tag(name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        client.start_model_server(server_name=server_name, tag=tag)
    click.echo("Successfully started model server {}".format(name))


@model_servers.command(name="stop", short_help="Stop a model server",
                       help="""Stop the model server with the specified NAME""")
@click.pass_context
@click.argument("name")
def stop(ctx, name):
    server_name, tag = get_name_and_tag(name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        client.stop_model_server(server_name=server_name, tag=tag)
    click.echo("Successfully stopped model server {}".format(name))


@model_servers.command(name="update", short_help="Update a model server with new configuration",
                       help="""Update the model server with the specified NAME to have a new configuration""")
@click.pass_context
@click.argument("name")
@click.argument("path")
def update(ctx, name, path):
    server_name, tag = get_name_and_tag(name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        client.update_model_server(server_name=server_name, tag=tag, path=path)
    click.echo("Successfully updated model server {}. Starting rolling updates to servers...".format(name))


# Doc: https://docs.google.com/document/d/1DgLLe8zOz5Omdb9YETKW1w0oWmTNoMZbQGD-NG7B2uo
@model_servers.command(name="apply", short_help="Update model servers based on a user-specified YAML file",
                       help="\b\nCreate/update/delete multiple model servers with a YAML file"
                            "\b\nProperties:"
                            "\b\n   specifier   REQUIRED (ex: image_classifier:v1)"
                            "\b\n   path        REQUIRED (ex: runs/8/mymodel.pt)"
                            "\b\n   type        OPTIONAL "
                            "(ex: tensorflow OR pytorch. Use auto-detected type if not specified)"
                            "\b\n   owner       OPTIONAL "
                            "(Uses this value if specified, if not then cmd line argument is used if specified,"
                            " and finally current active spell owner is used as a default if neither is specified)"
                            "\b\n   clusterName OPTIONAL "
                            "(Uses this value if specified, if not then cmd line argument is used if specified."
                            " If neither is specified, the spell owner should have exactly ONE cluster,"
                            " which will be used as default)")
@click.pass_context
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
@click.option("--delete", "-d", is_flag=True,
              help="Delete any currently existing model servers in this cluster "
                   "that are missing from the YAML file")
@click.option("--owner", type=str,
              help="Default owner for model servers unspecified in the YAML file. "
                   "Only use if you would like to specify an alternative owner to the currently active one.")
@click.option("--cluster-name", type=str,
              help="""Default cluster name for model servers unspecified in the YAML file""")
def apply(ctx, path, delete, owner, cluster_name):
    required_props = ["specifier", "path"]
    # Get current model server list
    client = ctx.obj["client"]
    model_servers = client.get_model_servers()
    # Store specifier-path pairs in a map
    model_server_map = dict()  # Key: specifier; Value: path
    for ms in model_servers:
        model_server_map[ms.get_specifier()] = ms.resource_path
    # Read configurations from yaml file
    config_specifier_set = set()
    with open(path, 'r') as stream:
        try:
            configs = yaml.safe_load_all(stream)
            for config in configs:
                # Check if the configuration contains required props
                for prop in required_props:
                    if prop not in config:
                        raise ExitException("'{}' is required. Please double check your YAML file.".format(prop))
                # Store all specifiers from the configurations
                config_specifier_set.add(config["specifier"])
                # Compare configurations in yaml file with current model server list
                if config["specifier"] in model_server_map:
                    # Update model servers whose path is different from as defined in YAML file
                    if config["path"] != model_server_map[config["specifier"]]:
                        server_name, tag, owner_new, _ = getConfigInfo(config, owner, cluster_name)
                        with api_client_exception_handler():
                            client.update_model_server(server_name=server_name,
                                                       tag=tag, path=config["path"], owner=owner_new)
                        click.echo("Successfully updated model server {}. "
                                   "Starting rolling updates to servers...".format(config["specifier"]))
                else:
                    # Create new model server
                    server_name, tag, owner_new, cluster_name_new = getConfigInfo(config, owner, cluster_name)
                    with api_client_exception_handler():
                        client.new_model_server(server_name=server_name,
                                                tag=tag,
                                                path=config["path"],
                                                type=config["type"] if "type" in config else None,
                                                cluster_name=cluster_name_new,
                                                owner=owner_new)
                    click.echo("Successfully created model server: {}".format(config["specifier"]))
        except yaml.YAMLError as exc:
            raise ExitException("Your YAML file contains invalid syntax! Please fix and try again: {}".format(exc))
    # Delete model servers not listed in the yaml file
    if delete:
        for specifier in model_server_map.keys():
            if specifier in config_specifier_set:
                continue
            server_name, tag = get_name_and_tag(specifier)
            with api_client_exception_handler():
                client.delete_model_server(server_name=server_name, tag=tag)
            click.echo("Successfully removed model server {}".format(specifier))


@model_servers.command(name="info", short_help="Get info about a model server",
                       help="""Get info about the model server with the specified NAME""")
@click.pass_context
@click.argument("name")
def get(ctx, name):
    server_name, tag = get_name_and_tag(name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        ms = client.get_model_server(server_name=server_name, tag=tag)

    lines = []
    lines.append(('Model Name', ms.server_name))
    lines.append(('Model Tag', ms.tag))
    lines.append(('Resource', ms.resource_path))
    lines.append(('Type', ms.type))
    lines.append(('Date Created', convert_to_local_time(ms.created_at)))
    lines.append(('Status', ms.status))
    lines.append(('Time Running', ms.get_age()))
    lines.append(('URL', ms.url))
    if ms.cluster:
        lines.append(('*NOTE*', "This will only be accessible within the same VPC of the cluster"))
    else:
        lines.append(('Access Token', ms.access_token))

    tabulate_rows(lines)


@model_servers.command(name="renew-token", short_help="Renews the access token for model server",
                       help="""Renews the access token for model server with the specified NAME""")
@click.pass_context
@click.argument("name")
def renew_token(ctx, name):
    server_name, tag = get_name_and_tag(name)
    client = ctx.obj["client"]
    with api_client_exception_handler():
        ms = client.renew_model_server_token(server_name=server_name, tag=tag)
    click.echo("New access token: {}".format(ms.access_token))


@model_servers.command(name="logs", short_help="Get logs from a model server",
                       help="""Get logs for the model server with the specified NAME""")
@click.pass_context
@click.option("-f", "--follow", is_flag=True,
              help="Follow log output")
@click.argument("name")
def logs(ctx, name, follow):
    server_name, tag = get_name_and_tag(name)
    client = ctx.obj["client"]
    utf8 = ctx.obj["utf8"]
    with api_client_exception_handler():
        try:
            for entry in client.get_model_server_log_entries(server_name, tag, follow=follow):
                click.echo(entry.log)
        except KeyboardInterrupt:
            if follow:
                click.echo()
                click.echo(with_emoji(u"✨", "Use 'spell model-servers logs -f {}' to view logs again".format(name),
                                      utf8))


def get_name_and_tag(specifier):
    name_tag = specifier.split(":")
    if len(name_tag) != 2:
        raise ExitException("Invalid name {}. Expected <model_name>:<tag> format.".format(specifier))
    name, tag = name_tag[0], name_tag[1]
    if not is_valid_specifier_part(name) or not is_valid_specifier_part(tag):
        raise ExitException("Invalid name {}".format(specifier))
    return (name, tag)


def is_valid_specifier_part(part):
    return re.match(r"^\w+[\w\.-]*", part)


def getConfigInfo(config, owner, cluster_name):
    server_name, tag = get_name_and_tag(config["specifier"])
    owner = owner if "owner" not in config else config["owner"]
    cluster_name = cluster_name if "clusterName" not in config else config["clusterName"]
    return server_name, tag, owner, cluster_name
