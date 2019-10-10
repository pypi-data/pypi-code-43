# -*- coding: utf-8 -*-
import click
import json
from ..utils.spinner import (
    init_spinner,
    start_spinner,
    stop_spinner,
)
from ..utils.print import (
    tbprint,
    eprint,
    oprint,
    opprint,
)


@click.group()
@click.pass_obj
@click.pass_context
def command_runner(ctx, obj):
    """DNA Center Command Runner API (version: 1.2.10).

    Wraps the DNA Center Command Runner API and exposes the API as native Python commands.

    """
    ctx.obj = obj.command_runner


@command_runner.command()
@click.option('--headers', type=str, help='''Dictionary of HTTP Headers to send with the Request.''',
              default=None,
              show_default=True)
@click.option('--payload', type=str, help='''A JSON serializable Python object to send in the body of the Request.''',
              default=None,
              show_default=True)
@click.option('--active_validation', type=bool, help='''Enable/Disable payload validation.''',
              default=True,
              show_default=True)
@click.option('-pp', '--pretty_print', type=int, help='''Pretty print indent''',
              default=None,
              show_default=True)
@click.option('--beep', is_flag=True, help='''Spinner beep (on)''')
@click.pass_obj
def get_all_keywords_of_clis_accepted(obj, pretty_print, beep,
                                      headers,
                                      payload,
                                      active_validation):
    """Get valid keywords.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_all_keywords_of_clis_accepted(
            headers=headers,
            payload=payload,
            active_validation=active_validation)
        stop_spinner(spinner)
        opprint(result, indent=pretty_print)
    except Exception as e:
        stop_spinner(spinner)
        tbprint()
        eprint('Error:', e)
        click.Context.exit(-1)


@command_runner.command()
@click.option('--commands', type=str, multiple=True,
              help='''CommandRunnerDTO's commands (list of strings).''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''CommandRunnerDTO's description.''',
              default=None,
              show_default=True)
@click.option('--deviceuuids', type=str, multiple=True,
              help='''CommandRunnerDTO's deviceUuids (list of strings).''',
              default=None,
              show_default=True)
@click.option('--name', type=str,
              help='''CommandRunnerDTO's name.''',
              default=None,
              show_default=True)
@click.option('--timeout', type=int,
              help='''CommandRunnerDTO's timeout.''',
              default=None,
              show_default=True)
@click.option('--headers', type=str, help='''Dictionary of HTTP Headers to send with the Request.''',
              default=None,
              show_default=True)
@click.option('--payload', type=str, help='''A JSON serializable Python object to send in the body of the Request.''',
              default=None,
              show_default=True)
@click.option('--active_validation', type=bool, help='''Enable/Disable payload validation.''',
              default=True,
              show_default=True)
@click.option('-pp', '--pretty_print', type=int, help='''Pretty print indent''',
              default=None,
              show_default=True)
@click.option('--beep', is_flag=True, help='''Spinner beep (on)''')
@click.pass_obj
def run_read_only_commands_on_devices(obj, pretty_print, beep,
                                      commands,
                                      description,
                                      deviceuuids,
                                      name,
                                      timeout,
                                      headers,
                                      payload,
                                      active_validation):
    """Submit request for read-only CLIs.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        commands = list(commands)
        commands = commands if len(commands) > 0 else None
        deviceuuids = list(deviceuuids)
        deviceuuids = deviceuuids if len(deviceuuids) > 0 else None
        result = obj.run_read_only_commands_on_devices(
            commands=commands,
            description=description,
            deviceUuids=deviceuuids,
            name=name,
            timeout=timeout,
            headers=headers,
            payload=payload,
            active_validation=active_validation)
        stop_spinner(spinner)
        opprint(result, indent=pretty_print)
    except Exception as e:
        stop_spinner(spinner)
        tbprint()
        eprint('Error:', e)
        click.Context.exit(-1)
