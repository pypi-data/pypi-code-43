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
def swim(ctx, obj):
    """DNA Center SWIM API (version: 1.3.0).

    Wraps the DNA Center SWIM API and exposes the API as native Python commands.

    """
    ctx.obj = obj.swim


@swim.command()
@click.option('--image_uuid', type=str,
              help='''imageUuid query parameter.''',
              show_default=True)
@click.option('--name', type=str,
              help='''name query parameter.''',
              show_default=True)
@click.option('--family', type=str,
              help='''family query parameter.''',
              show_default=True)
@click.option('--application_type', type=str,
              help='''applicationType query parameter.''',
              show_default=True)
@click.option('--image_integrity_status', type=str,
              help='''imageIntegrityStatus - FAILURE, UNKNOWN, VERIFIED.''',
              show_default=True)
@click.option('--version', type=str,
              help='''software Image Version.''',
              show_default=True)
@click.option('--image_series', type=str,
              help='''image Series.''',
              show_default=True)
@click.option('--image_name', type=str,
              help='''image Name.''',
              show_default=True)
@click.option('--is_tagged_golden', type=bool,
              help='''is Tagged Golden.''',
              show_default=True)
@click.option('--is_cco_recommended', type=bool,
              help='''is recommended from cisco.com.''',
              show_default=True)
@click.option('--is_cco_latest', type=bool,
              help='''is latest from cisco.com.''',
              show_default=True)
@click.option('--created_time', type=int,
              help='''time in milliseconds (epoch format).''',
              show_default=True)
@click.option('--image_size_greater_than', type=int,
              help='''size in bytes.''',
              show_default=True)
@click.option('--image_size_lesser_than', type=int,
              help='''size in bytes.''',
              show_default=True)
@click.option('--sort_by', type=str,
              help='''sort results by this field.''',
              show_default=True)
@click.option('--sort_order', type=str,
              help='''sort order - 'asc' or 'des'. Default is asc.''',
              show_default=True)
@click.option('--limit', type=int,
              help='''limit query parameter.''',
              show_default=True)
@click.option('--offset', type=int,
              help='''offset query parameter.''',
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
def get_software_image_details(obj, pretty_print, beep,
                               image_uuid,
                               name,
                               family,
                               application_type,
                               image_integrity_status,
                               version,
                               image_series,
                               image_name,
                               is_tagged_golden,
                               is_cco_recommended,
                               is_cco_latest,
                               created_time,
                               image_size_greater_than,
                               image_size_lesser_than,
                               sort_by,
                               sort_order,
                               limit,
                               offset,
                               headers,
                               payload,
                               active_validation):
    """Returns software image list based on a filter criteria. For example: "filterbyName = cat3k%".
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_software_image_details(
            image_uuid=image_uuid,
            name=name,
            family=family,
            application_type=application_type,
            image_integrity_status=image_integrity_status,
            version=version,
            image_series=image_series,
            image_name=image_name,
            is_tagged_golden=is_tagged_golden,
            is_cco_recommended=is_cco_recommended,
            is_cco_latest=is_cco_latest,
            created_time=created_time,
            image_size_greater_than=image_size_greater_than,
            image_size_lesser_than=image_size_lesser_than,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
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


@swim.command()
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
def trigger_software_image_distribution(obj, pretty_print, beep,
                                        headers,
                                        payload,
                                        active_validation):
    """Distributes a software image on a given device. Software image must be imported successfully into DNA Center before it can be distributed.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.trigger_software_image_distribution(
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


@swim.command()
@click.option('--is_third_party', type=bool,
              help='''Third party Image check.''',
              show_default=True)
@click.option('--third_party_vendor', type=str,
              help='''Third Party Vendor.''',
              show_default=True)
@click.option('--third_party_image_family', type=str,
              help='''Third Party image family.''',
              show_default=True)
@click.option('--third_party_application_type', type=str,
              help='''Third Party Application Type.''',
              show_default=True)
@click.option('--file', type=click.File('rb'),
              help='The full path of a file. The file is opened with rb flag.',
              required=True,
              show_default=True)
@click.option('--filename', type=str,
              help='The filename (with its extension, for example, test.zip)',
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
def import_local_software_image(obj, pretty_print, beep,
                                is_third_party,
                                third_party_vendor,
                                third_party_image_family,
                                third_party_application_type,
                                file,
                                filename,
                                headers,
                                payload,
                                active_validation):
    """Fetches a software image from local file system and uploads to DNA Center. Supported software image files extensions are bin, img, tar, smu, pie, aes, iso, ova, tar_gz and qcow2.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.import_local_software_image(
            is_third_party=is_third_party,
            third_party_vendor=third_party_vendor,
            third_party_image_family=third_party_image_family,
            third_party_application_type=third_party_application_type,
            multipart_fields={'file': (filename, file)},
            multipart_monitor_callback=None,
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


@swim.command()
@click.option('--schedule_validate', type=bool,
              help='''scheduleValidate, validates data before schedule (Optional).''',
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
def trigger_software_image_activation(obj, pretty_print, beep,
                                      schedule_validate,
                                      headers,
                                      payload,
                                      active_validation):
    """Activates a software image on a given device. Software image must be present in the device flash.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.trigger_software_image_activation(
            schedule_validate=schedule_validate,
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


@swim.command()
@click.option('--schedule_at', type=str,
              help='''Epoch Time (The number of milli-seconds since January 1 1970 UTC) at which the distribution should be scheduled (Optional) .''',
              show_default=True)
@click.option('--schedule_desc', type=str,
              help='''Custom Description (Optional).''',
              show_default=True)
@click.option('--schedule_origin', type=str,
              help='''Originator of this call (Optional).''',
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
def import_software_image_via_url(obj, pretty_print, beep,
                                  schedule_at,
                                  schedule_desc,
                                  schedule_origin,
                                  headers,
                                  payload,
                                  active_validation):
    """Fetches a software image from remote file system (using URL for HTTP/FTP) and uploads to DNA Center. Supported image files extensions are bin, img, tar, smu, pie, aes, iso, ova, tar_gz and qcow2.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.import_software_image_via_url(
            schedule_at=schedule_at,
            schedule_desc=schedule_desc,
            schedule_origin=schedule_origin,
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
