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
def site_profile(ctx, obj):
    """DNA Center Site Profile API (version: 1.2.10).

    Wraps the DNA Center Site Profile API and exposes the API as native Python commands.

    """
    ctx.obj = obj.site_profile


@site_profile.command()
@click.option('--device_ip', type=str,
              help='''Device to which the provisioning detail has to be retrieved.''',
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
def get_device_details_by_ip(obj, pretty_print, beep,
                             device_ip,
                             headers,
                             payload,
                             active_validation):
    """**Beta** - Returns provisioning device information for the specified IP address.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_details_by_ip(
            device_ip=device_ip,
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


@site_profile.command()
@click.option('--callbackurl', type=str,
              help='''Callback Url, property of the request body.''',
              default=None,
              show_default=True)
@click.option('--provisioning', type=str, multiple=True,
              help='''Provisioning, property of the request body (list of objects).''',
              default=None,
              show_default=True)
@click.option('--siteprofile', type=str, multiple=True,
              help='''Site Profile, property of the request body (list of objects).''',
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
def provision_nfv(obj, pretty_print, beep,
                  callbackurl,
                  provisioning,
                  siteprofile,
                  headers,
                  payload,
                  active_validation):
    """Design and Provision single/multi NFV device with given site/area/building/floor .
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        provisioning = list(provisioning)
        provisioning = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in provisioning)))
        provisioning = provisioning if len(provisioning) > 0 else None
        siteprofile = list(siteprofile)
        siteprofile = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in siteprofile)))
        siteprofile = siteprofile if len(siteprofile) > 0 else None
        result = obj.provision_nfv(
            callbackUrl=callbackurl,
            provisioning=provisioning,
            siteProfile=siteprofile,
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
