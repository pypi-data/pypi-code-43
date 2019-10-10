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
def path_trace(ctx, obj):
    """DNA Center Path Trace API (version: 1.3.0).

    Wraps the DNA Center Path Trace API and exposes the API as native Python commands.

    """
    ctx.obj = obj.path_trace


@path_trace.command()
@click.option('--periodic_refresh', type=bool,
              help='''Is analysis periodically refreshed?.''',
              show_default=True)
@click.option('--source_ip', type=str,
              help='''Source IP address.''',
              show_default=True)
@click.option('--dest_ip', type=str,
              help='''Destination IP adress.''',
              show_default=True)
@click.option('--source_port', type=str,
              help='''Source port.''',
              show_default=True)
@click.option('--dest_port', type=str,
              help='''Destination port.''',
              show_default=True)
@click.option('--gt_create_time', type=str,
              help='''Analyses requested after this time.''',
              show_default=True)
@click.option('--lt_create_time', type=str,
              help='''Analyses requested before this time.''',
              show_default=True)
@click.option('--protocol', type=str,
              help='''protocol query parameter.''',
              show_default=True)
@click.option('--status', type=str,
              help='''status query parameter.''',
              show_default=True)
@click.option('--task_id', type=str,
              help='''Task ID.''',
              show_default=True)
@click.option('--last_update_time', type=str,
              help='''Last update time.''',
              show_default=True)
@click.option('--limit', type=str,
              help='''Number of resources returned.''',
              show_default=True)
@click.option('--offset', type=str,
              help='''Start index of resources returned (1-based).''',
              show_default=True)
@click.option('--order', type=str,
              help='''Order by this field.''',
              show_default=True)
@click.option('--sort_by', type=str,
              help='''Sort by this field.''',
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
def retrives_all_previous_pathtraces_summary(obj, pretty_print, beep,
                                             periodic_refresh,
                                             source_ip,
                                             dest_ip,
                                             source_port,
                                             dest_port,
                                             gt_create_time,
                                             lt_create_time,
                                             protocol,
                                             status,
                                             task_id,
                                             last_update_time,
                                             limit,
                                             offset,
                                             order,
                                             sort_by,
                                             headers,
                                             payload,
                                             active_validation):
    """Returns a summary of all flow analyses stored. Results can be filtered by specified parameters.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.retrives_all_previous_pathtraces_summary(
            periodic_refresh=periodic_refresh,
            source_ip=source_ip,
            dest_ip=dest_ip,
            source_port=source_port,
            dest_port=dest_port,
            gt_create_time=gt_create_time,
            lt_create_time=lt_create_time,
            protocol=protocol,
            status=status,
            task_id=task_id,
            last_update_time=last_update_time,
            limit=limit,
            offset=offset,
            order=order,
            sort_by=sort_by,
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


@path_trace.command()
@click.option('--flow_analysis_id', type=str,
              help='''Flow analysis request id.''',
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
def retrieves_previous_pathtrace(obj, pretty_print, beep,
                                 flow_analysis_id,
                                 headers,
                                 payload,
                                 active_validation):
    """Returns result of a previously requested flow analysis by its Flow Analysis id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.retrieves_previous_pathtrace(
            flow_analysis_id=flow_analysis_id,
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


@path_trace.command()
@click.option('--flow_analysis_id', type=str,
              help='''Flow analysis request id.''',
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
def deletes_pathtrace_by_id(obj, pretty_print, beep,
                            flow_analysis_id,
                            headers,
                            payload,
                            active_validation):
    """Deletes a flow analysis request by its id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.deletes_pathtrace_by_id(
            flow_analysis_id=flow_analysis_id,
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


@path_trace.command()
@click.option('--controlpath', type=bool,
              help='''FlowAnalysisRequest's controlPath.''',
              default=None,
              show_default=True)
@click.option('--destip', type=str,
              help='''FlowAnalysisRequest's destIP.''',
              default=None,
              show_default=True)
@click.option('--destport', type=str,
              help='''FlowAnalysisRequest's destPort.''',
              default=None,
              show_default=True)
@click.option('--inclusions', type=str, multiple=True,
              help='''FlowAnalysisRequest's inclusions (list of strings).''',
              default=None,
              show_default=True)
@click.option('--periodicrefresh', type=bool,
              help='''FlowAnalysisRequest's periodicRefresh.''',
              default=None,
              show_default=True)
@click.option('--protocol', type=str,
              help='''FlowAnalysisRequest's protocol.''',
              default=None,
              show_default=True)
@click.option('--sourceip', type=str,
              help='''FlowAnalysisRequest's sourceIP.''',
              default=None,
              show_default=True)
@click.option('--sourceport', type=str,
              help='''FlowAnalysisRequest's sourcePort.''',
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
def initiate_a_new_pathtrace(obj, pretty_print, beep,
                             controlpath,
                             destip,
                             destport,
                             inclusions,
                             periodicrefresh,
                             protocol,
                             sourceip,
                             sourceport,
                             headers,
                             payload,
                             active_validation):
    """Initiates a new flow analysis with periodic refresh and stat collection options. Returns a request id and a task id to get results and follow progress.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        inclusions = list(inclusions)
        inclusions = inclusions if len(inclusions) > 0 else None
        result = obj.initiate_a_new_pathtrace(
            controlPath=controlpath,
            destIP=destip,
            destPort=destport,
            inclusions=inclusions,
            periodicRefresh=periodicrefresh,
            protocol=protocol,
            sourceIP=sourceip,
            sourcePort=sourceport,
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
