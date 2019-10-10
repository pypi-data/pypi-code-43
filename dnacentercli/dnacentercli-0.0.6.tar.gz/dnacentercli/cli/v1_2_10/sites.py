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
def sites(ctx, obj):
    """DNA Center Sites API (version: 1.2.10).

    Wraps the DNA Center Sites API and exposes the API as native Python commands.

    """
    ctx.obj = obj.sites


@sites.command()
@click.option('--timestamp', type=str,
              help='''Epoch time(in milliseconds) when the Site Hierarchy data is required.''',
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
def get_site_health(obj, pretty_print, beep,
                    timestamp,
                    headers,
                    payload,
                    active_validation):
    """Returns Overall Health information for all sites.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_site_health(
            timestamp=timestamp,
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


@sites.command()
@click.option('--device', type=str, multiple=True,
              help='''Device, property of the request body (list of objects).''',
              default=None,
              show_default=True)
@click.option('--site_id', type=str,
              help='''Site id to which the device is assigned.''',
              required=True,
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
def assign_device_to_site(obj, pretty_print, beep,
                          device,
                          site_id,
                          headers,
                          payload,
                          active_validation):
    """Assigns list of devices to a site.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        device = list(device)
        device = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in device)))
        device = device if len(device) > 0 else None
        result = obj.assign_device_to_site(
            device=device,
            site_id=site_id,
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


@sites.command()
@click.option('--site', type=str,
              help='''Site, property of the request body.''',
              default=None,
              show_default=True)
@click.option('--type', type=str,
              help='''Type, property of the request body. Available values are 'area', 'building' and 'floor'.''',
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
def create_site(obj, pretty_print, beep,
                site,
                type,
                headers,
                payload,
                active_validation):
    """Creates site with area/building/floor with specified hierarchy.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        if site is not None:
            site = json.loads('{}'.format(site))
        result = obj.create_site(
            site=site,
            type=type,
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
