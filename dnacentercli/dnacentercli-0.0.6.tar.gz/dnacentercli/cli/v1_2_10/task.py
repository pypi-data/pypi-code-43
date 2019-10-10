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
def task(ctx, obj):
    """DNA Center Task API (version: 1.2.10).

    Wraps the DNA Center Task API and exposes the API as native Python commands.

    """
    ctx.obj = obj.task


@task.command()
@click.option('--start_time', type=str,
              help='''This is the epoch start time from which tasks need to be fetched.''',
              show_default=True)
@click.option('--end_time', type=str,
              help='''This is the epoch end time upto which audit records need to be fetched.''',
              show_default=True)
@click.option('--data', type=str,
              help='''Fetch tasks that contains this data.''',
              show_default=True)
@click.option('--error_code', type=str,
              help='''Fetch tasks that have this error code.''',
              show_default=True)
@click.option('--service_type', type=str,
              help='''Fetch tasks with this service type.''',
              show_default=True)
@click.option('--username', type=str,
              help='''Fetch tasks with this username.''',
              show_default=True)
@click.option('--progress', type=str,
              help='''Fetch tasks that contains this progress.''',
              show_default=True)
@click.option('--is_error', type=str,
              help='''Fetch tasks ended as success or failure. Valid valuestrue, false.''',
              show_default=True)
@click.option('--failure_reason', type=str,
              help='''Fetch tasks that contains this failure reason.''',
              show_default=True)
@click.option('--parent_id', type=str,
              help='''Fetch tasks that have this parent Id.''',
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
def get_task_count(obj, pretty_print, beep,
                   start_time,
                   end_time,
                   data,
                   error_code,
                   service_type,
                   username,
                   progress,
                   is_error,
                   failure_reason,
                   parent_id,
                   headers,
                   payload,
                   active_validation):
    """Returns Task count.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_task_count(
            start_time=start_time,
            end_time=end_time,
            data=data,
            error_code=error_code,
            service_type=service_type,
            username=username,
            progress=progress,
            is_error=is_error,
            failure_reason=failure_reason,
            parent_id=parent_id,
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


@task.command()
@click.option('--task_id', type=str,
              help='''UUID of the Task.''',
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
def get_task_by_id(obj, pretty_print, beep,
                   task_id,
                   headers,
                   payload,
                   active_validation):
    """Returns a task by specified id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_task_by_id(
            task_id=task_id,
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


@task.command()
@click.option('--start_time', type=str,
              help='''This is the epoch start time from which tasks need to be fetched.''',
              show_default=True)
@click.option('--end_time', type=str,
              help='''This is the epoch end time upto which audit records need to be fetched.''',
              show_default=True)
@click.option('--data', type=str,
              help='''Fetch tasks that contains this data.''',
              show_default=True)
@click.option('--error_code', type=str,
              help='''Fetch tasks that have this error code.''',
              show_default=True)
@click.option('--service_type', type=str,
              help='''Fetch tasks with this service type.''',
              show_default=True)
@click.option('--username', type=str,
              help='''Fetch tasks with this username.''',
              show_default=True)
@click.option('--progress', type=str,
              help='''Fetch tasks that contains this progress.''',
              show_default=True)
@click.option('--is_error', type=str,
              help='''Fetch tasks ended as success or failure. Valid valuestrue, false.''',
              show_default=True)
@click.option('--failure_reason', type=str,
              help='''Fetch tasks that contains this failure reason.''',
              show_default=True)
@click.option('--parent_id', type=str,
              help='''Fetch tasks that have this parent Id.''',
              show_default=True)
@click.option('--offset', type=str,
              help='''offset query parameter.''',
              show_default=True)
@click.option('--limit', type=str,
              help='''limit query parameter.''',
              show_default=True)
@click.option('--sort_by', type=str,
              help='''Sort results by this field.''',
              show_default=True)
@click.option('--order', type=str,
              help='''Sort order - asc or dsc.''',
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
def get_tasks(obj, pretty_print, beep,
              start_time,
              end_time,
              data,
              error_code,
              service_type,
              username,
              progress,
              is_error,
              failure_reason,
              parent_id,
              offset,
              limit,
              sort_by,
              order,
              headers,
              payload,
              active_validation):
    """Returns task(s) based on filter criteria.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_tasks(
            start_time=start_time,
            end_time=end_time,
            data=data,
            error_code=error_code,
            service_type=service_type,
            username=username,
            progress=progress,
            is_error=is_error,
            failure_reason=failure_reason,
            parent_id=parent_id,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            order=order,
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


@task.command()
@click.option('--task_id', type=str,
              help='''UUID of the Task.''',
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
def get_task_tree(obj, pretty_print, beep,
                  task_id,
                  headers,
                  payload,
                  active_validation):
    """Returns a task with its children tasks by based on their id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_task_tree(
            task_id=task_id,
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


@task.command()
@click.option('--operation_id', type=str,
              help='''operationId path parameter.''',
              required=True,
              show_default=True)
@click.option('--offset', type=int,
              help='''Index, minimum value is 0.''',
              required=True,
              show_default=True)
@click.option('--limit', type=int,
              help='''The maximum value of {limit} supported is 500.
             Base 1 indexing for {limit}, minimum value is 1.''',
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
def get_task_by_operationid(obj, pretty_print, beep,
                            operation_id,
                            offset,
                            limit,
                            headers,
                            payload,
                            active_validation):
    """Returns root tasks associated with an Operationid.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_task_by_operationid(
            operation_id=operation_id,
            offset=offset,
            limit=limit,
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
