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
def devices(ctx, obj):
    """DNA Center Devices API (version: 1.2.10).

    Wraps the DNA Center Devices API and exposes the API as native Python commands.

    """
    ctx.obj = obj.devices


@devices.command()
@click.option('--id', type=str,
              help='''Module UUID.''',
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
def get_module_info_by_id(obj, pretty_print, beep,
                          id,
                          headers,
                          payload,
                          active_validation):
    """Returns Module info by id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_module_info_by_id(
            id=id,
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


@devices.command()
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
def get_device_interface_count(obj, pretty_print, beep,
                               headers,
                               payload,
                               active_validation):
    """Returns the count of interfaces for all devices.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_interface_count(
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


@devices.command()
@click.option('--force_sync', type=bool,
              help='''forceSync query parameter.''',
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
def sync_devices_using_forcesync(obj, pretty_print, beep,
                                 force_sync,
                                 headers,
                                 payload,
                                 active_validation):
    """Synchronizes the devices. If forceSync param is false (default) then the sync would run in normal priority thread. If forceSync param is true then the sync would run in high priority thread if available, else the sync will fail. Result can be seen in the child task of each device.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.sync_devices_using_forcesync(
            force_sync=force_sync,
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


@devices.command()
@click.option('--hostname', type=str,
              help='''hostname query parameter.''',
              show_default=True)
@click.option('--management_ip_address', type=str,
              help='''managementIpAddress query parameter.''',
              show_default=True)
@click.option('--mac_address', type=str,
              help='''macAddress query parameter.''',
              show_default=True)
@click.option('--location_name', type=str,
              help='''locationName query parameter.''',
              show_default=True)
@click.option('--serial_number', type=str,
              help='''serialNumber query parameter.''',
              show_default=True)
@click.option('--location', type=str,
              help='''location query parameter.''',
              show_default=True)
@click.option('--family', type=str,
              help='''family query parameter.''',
              show_default=True)
@click.option('--type', type=str,
              help='''type query parameter.''',
              show_default=True)
@click.option('--series', type=str,
              help='''series query parameter.''',
              show_default=True)
@click.option('--collection_status', type=str,
              help='''collectionStatus query parameter.''',
              show_default=True)
@click.option('--collection_interval', type=str,
              help='''collectionInterval query parameter.''',
              show_default=True)
@click.option('--not_synced_for_minutes', type=str,
              help='''notSyncedForMinutes query parameter.''',
              show_default=True)
@click.option('--error_code', type=str,
              help='''errorCode query parameter.''',
              show_default=True)
@click.option('--error_description', type=str,
              help='''errorDescription query parameter.''',
              show_default=True)
@click.option('--software_version', type=str,
              help='''softwareVersion query parameter.''',
              show_default=True)
@click.option('--software_type', type=str,
              help='''softwareType query parameter.''',
              show_default=True)
@click.option('--platform_id', type=str,
              help='''platformId query parameter.''',
              show_default=True)
@click.option('--role', type=str,
              help='''role query parameter.''',
              show_default=True)
@click.option('--reachability_status', type=str,
              help='''reachabilityStatus query parameter.''',
              show_default=True)
@click.option('--up_time', type=str,
              help='''upTime query parameter.''',
              show_default=True)
@click.option('--associated_wlc_ip', type=str,
              help='''associatedWlcIp query parameter.''',
              show_default=True)
@click.option('--license_name', type=str,
              help='''license.name query parameter.''',
              show_default=True)
@click.option('--license_type', type=str,
              help='''license.type query parameter.''',
              show_default=True)
@click.option('--license_status', type=str,
              help='''license.status query parameter.''',
              show_default=True)
@click.option('--module_name', type=str,
              help='''module+name query parameter.''',
              show_default=True)
@click.option('--module_equpimenttype', type=str,
              help='''module+equpimenttype query parameter.''',
              show_default=True)
@click.option('--module_servicestate', type=str,
              help='''module+servicestate query parameter.''',
              show_default=True)
@click.option('--module_vendorequipmenttype', type=str,
              help='''module+vendorequipmenttype query parameter.''',
              show_default=True)
@click.option('--module_partnumber', type=str,
              help='''module+partnumber query parameter.''',
              show_default=True)
@click.option('--module_operationstatecode', type=str,
              help='''module+operationstatecode query parameter.''',
              show_default=True)
@click.option('--id', type=str,
              help='''Accepts comma separated id's and return list of network-devices for the given id's. If invalid or not-found id's are provided, null entry will be returned in the list.''',
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
def get_device_list(obj, pretty_print, beep,
                    hostname,
                    management_ip_address,
                    mac_address,
                    location_name,
                    serial_number,
                    location,
                    family,
                    type,
                    series,
                    collection_status,
                    collection_interval,
                    not_synced_for_minutes,
                    error_code,
                    error_description,
                    software_version,
                    software_type,
                    platform_id,
                    role,
                    reachability_status,
                    up_time,
                    associated_wlc_ip,
                    license_name,
                    license_type,
                    license_status,
                    module_name,
                    module_equpimenttype,
                    module_servicestate,
                    module_vendorequipmenttype,
                    module_partnumber,
                    module_operationstatecode,
                    id,
                    headers,
                    payload,
                    active_validation):
    """Returns list of network devices based on filter criteria such as management IP address, mac address, hostname, location name and a wide variety of additional criteria. You can also use the asterisk in any value to conduct a wildcard search. For example, to find all hostnames beginning with myhost in the IP address range 192.25.18.n, issue the following request: GET  fqdnoripofdnacenterplatform/dna/intent/api/v1/network-device? hostname=myhost* & managementIpAddress=192.25.18.* For a complete list of parameter names that you can use for filtering this request, see the DNA Center API Reference documentation.  Note: If id parameter is provided, it will return the list of network-devices for the given ids and ignores the other request parameters. .
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_list(
            hostname=hostname,
            management_ip_address=management_ip_address,
            mac_address=mac_address,
            location_name=location_name,
            serial_number=serial_number,
            location=location,
            family=family,
            type=type,
            series=series,
            collection_status=collection_status,
            collection_interval=collection_interval,
            not_synced_for_minutes=not_synced_for_minutes,
            error_code=error_code,
            error_description=error_description,
            software_version=software_version,
            software_type=software_type,
            platform_id=platform_id,
            role=role,
            reachability_status=reachability_status,
            up_time=up_time,
            associated_wlc_ip=associated_wlc_ip,
            license_name=license_name,
            license_type=license_type,
            license_status=license_status,
            module_name=module_name,
            module_equpimenttype=module_equpimenttype,
            module_servicestate=module_servicestate,
            module_vendorequipmenttype=module_vendorequipmenttype,
            module_partnumber=module_partnumber,
            module_operationstatecode=module_operationstatecode,
            id=id,
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


@devices.command()
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
def get_polling_interval_for_all_devices(obj, pretty_print, beep,
                                         headers,
                                         payload,
                                         active_validation):
    """Returns polling interval of all devices.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_polling_interval_for_all_devices(
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


@devices.command()
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
def get_device_count(obj, pretty_print, beep,
                     headers,
                     payload,
                     active_validation):
    """Returns the count of network devices based on the filter criteria by management IP address, mac address, hostname and location name.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_count(
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


@devices.command()
@click.option('--interface_type', type=str,
              help='''Vlan assocaited with sub-interface.''',
              show_default=True)
@click.option('--id', type=str,
              help='''id path parameter.''',
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
def get_device_interface_vlans(obj, pretty_print, beep,
                               interface_type,
                               id,
                               headers,
                               payload,
                               active_validation):
    """Returns Device Interface VLANs.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_interface_vlans(
            interface_type=interface_type,
            id=id,
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


@devices.command()
@click.option('--device_id', type=str,
              help='''Device ID.''',
              required=True,
              show_default=True)
@click.option('--start_index', type=int,
              help='''Start index.''',
              required=True,
              show_default=True)
@click.option('--records_to_return', type=int,
              help='''Number of records to return.''',
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
def get_device_interfaces_by_specified_range(obj, pretty_print, beep,
                                             device_id,
                                             start_index,
                                             records_to_return,
                                             headers,
                                             payload,
                                             active_validation):
    """Returns the list of interfaces for the device for the specified range.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_interfaces_by_specified_range(
            device_id=device_id,
            start_index=start_index,
            records_to_return=records_to_return,
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


@devices.command()
@click.option('--is_force_delete', type=bool,
              help='''isForceDelete query parameter.''',
              show_default=True)
@click.option('--id', type=str,
              help='''Device ID.''',
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
def delete_device_by_id(obj, pretty_print, beep,
                        is_force_delete,
                        id,
                        headers,
                        payload,
                        active_validation):
    """Deletes the network device for the given Id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.delete_device_by_id(
            is_force_delete=is_force_delete,
            id=id,
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


@devices.command()
@click.option('--network_device_id', type=str,
              help='''networkDeviceId path parameter.''',
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
def get_device_config_by_id(obj, pretty_print, beep,
                            network_device_id,
                            headers,
                            payload,
                            active_validation):
    """Returns the device config by specified device ID.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_config_by_id(
            network_device_id=network_device_id,
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


@devices.command()
@click.option('--clitransport', type=str,
              help='''InventoryDeviceInfo's cliTransport.''',
              default=None,
              show_default=True)
@click.option('--computedevice', type=bool,
              help='''InventoryDeviceInfo's computeDevice.''',
              default=None,
              show_default=True)
@click.option('--enablepassword', type=str,
              help='''InventoryDeviceInfo's enablePassword.''',
              default=None,
              show_default=True)
@click.option('--extendeddiscoveryinfo', type=str,
              help='''InventoryDeviceInfo's extendedDiscoveryInfo.''',
              default=None,
              show_default=True)
@click.option('--httppassword', type=str,
              help='''InventoryDeviceInfo's httpPassword.''',
              default=None,
              show_default=True)
@click.option('--httpport', type=str,
              help='''InventoryDeviceInfo's httpPort.''',
              default=None,
              show_default=True)
@click.option('--httpsecure', type=bool,
              help='''InventoryDeviceInfo's httpSecure.''',
              default=None,
              show_default=True)
@click.option('--httpusername', type=str,
              help='''InventoryDeviceInfo's httpUserName.''',
              default=None,
              show_default=True)
@click.option('--ipaddress', type=str, multiple=True,
              help='''InventoryDeviceInfo's ipAddress (list of strings).''',
              default=None,
              show_default=True)
@click.option('--merakiorgid', type=str, multiple=True,
              help='''InventoryDeviceInfo's merakiOrgId (list of strings).''',
              default=None,
              show_default=True)
@click.option('--netconfport', type=str,
              help='''InventoryDeviceInfo's netconfPort.''',
              default=None,
              show_default=True)
@click.option('--password', type=str,
              help='''InventoryDeviceInfo's password.''',
              default=None,
              show_default=True)
@click.option('--serialnumber', type=str,
              help='''InventoryDeviceInfo's serialNumber.''',
              default=None,
              show_default=True)
@click.option('--snmpauthpassphrase', type=str,
              help='''InventoryDeviceInfo's snmpAuthPassphrase.''',
              default=None,
              show_default=True)
@click.option('--snmpauthprotocol', type=str,
              help='''InventoryDeviceInfo's snmpAuthProtocol.''',
              default=None,
              show_default=True)
@click.option('--snmpmode', type=str,
              help='''InventoryDeviceInfo's snmpMode.''',
              default=None,
              show_default=True)
@click.option('--snmpprivpassphrase', type=str,
              help='''InventoryDeviceInfo's snmpPrivPassphrase.''',
              default=None,
              show_default=True)
@click.option('--snmpprivprotocol', type=str,
              help='''InventoryDeviceInfo's snmpPrivProtocol.''',
              default=None,
              show_default=True)
@click.option('--snmprocommunity', type=str,
              help='''InventoryDeviceInfo's snmpROCommunity.''',
              default=None,
              show_default=True)
@click.option('--snmprwcommunity', type=str,
              help='''InventoryDeviceInfo's snmpRWCommunity.''',
              default=None,
              show_default=True)
@click.option('--snmpretry', type=int,
              help='''InventoryDeviceInfo's snmpRetry.''',
              default=None,
              show_default=True)
@click.option('--snmptimeout', type=int,
              help='''InventoryDeviceInfo's snmpTimeout.''',
              default=None,
              show_default=True)
@click.option('--snmpusername', type=str,
              help='''InventoryDeviceInfo's snmpUserName.''',
              default=None,
              show_default=True)
@click.option('--snmpversion', type=str,
              help='''InventoryDeviceInfo's snmpVersion.''',
              default=None,
              show_default=True)
@click.option('--type', type=str,
              help='''InventoryDeviceInfo's type. Available values are 'COMPUTE_DEVICE', 'MERAKI_DASHBOARD', 'NETWORK_DEVICE' and 'NODATACHANGE'.''',
              default=None,
              show_default=True)
@click.option('--updatemgmtipaddresslist', type=str, multiple=True,
              help='''InventoryDeviceInfo's updateMgmtIPaddressList (list of objects).''',
              default=None,
              show_default=True)
@click.option('--username', type=str,
              help='''InventoryDeviceInfo's userName.''',
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
def add_device(obj, pretty_print, beep,
               clitransport,
               computedevice,
               enablepassword,
               extendeddiscoveryinfo,
               httppassword,
               httpport,
               httpsecure,
               httpusername,
               ipaddress,
               merakiorgid,
               netconfport,
               password,
               serialnumber,
               snmpauthpassphrase,
               snmpauthprotocol,
               snmpmode,
               snmpprivpassphrase,
               snmpprivprotocol,
               snmprocommunity,
               snmprwcommunity,
               snmpretry,
               snmptimeout,
               snmpusername,
               snmpversion,
               type,
               updatemgmtipaddresslist,
               username,
               headers,
               payload,
               active_validation):
    """Adds the device with given credential.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        ipaddress = list(ipaddress)
        ipaddress = ipaddress if len(ipaddress) > 0 else None
        merakiorgid = list(merakiorgid)
        merakiorgid = merakiorgid if len(merakiorgid) > 0 else None
        updatemgmtipaddresslist = list(updatemgmtipaddresslist)
        updatemgmtipaddresslist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in updatemgmtipaddresslist)))
        updatemgmtipaddresslist = updatemgmtipaddresslist if len(updatemgmtipaddresslist) > 0 else None
        result = obj.add_device(
            cliTransport=clitransport,
            computeDevice=computedevice,
            enablePassword=enablepassword,
            extendedDiscoveryInfo=extendeddiscoveryinfo,
            httpPassword=httppassword,
            httpPort=httpport,
            httpSecure=httpsecure,
            httpUserName=httpusername,
            ipAddress=ipaddress,
            merakiOrgId=merakiorgid,
            netconfPort=netconfport,
            password=password,
            serialNumber=serialnumber,
            snmpAuthPassphrase=snmpauthpassphrase,
            snmpAuthProtocol=snmpauthprotocol,
            snmpMode=snmpmode,
            snmpPrivPassphrase=snmpprivpassphrase,
            snmpPrivProtocol=snmpprivprotocol,
            snmpROCommunity=snmprocommunity,
            snmpRWCommunity=snmprwcommunity,
            snmpRetry=snmpretry,
            snmpTimeout=snmptimeout,
            snmpUserName=snmpusername,
            snmpVersion=snmpversion,
            type=type,
            updateMgmtIPaddressList=updatemgmtipaddresslist,
            userName=username,
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


@devices.command()
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
def get_device_config_count(obj, pretty_print, beep,
                            headers,
                            payload,
                            active_validation):
    """Returns the count of device configs.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_config_count(
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


@devices.command()
@click.option('--name', type=str,
              help='''Interface name.''',
              required=True,
              show_default=True)
@click.option('--device_id', type=str,
              help='''Device ID.''',
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
def get_interface_details(obj, pretty_print, beep,
                          name,
                          device_id,
                          headers,
                          payload,
                          active_validation):
    """Returns interface by specified device Id and interface name.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_interface_details(
            name=name,
            device_id=device_id,
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


@devices.command()
@click.option('--id', type=str,
              help='''Device ID.''',
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
def get_polling_interval_by_id(obj, pretty_print, beep,
                               id,
                               headers,
                               payload,
                               active_validation):
    """Returns polling interval by device id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_polling_interval_by_id(
            id=id,
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


@devices.command()
@click.option('--device_id', type=str,
              help='''deviceId query parameter.''',
              required=True,
              show_default=True)
@click.option('--name_list', type=str,
              help='''nameList query parameter.''',
              show_default=True)
@click.option('--vendor_equipment_type_list', type=str,
              help='''vendorEquipmentTypeList query parameter.''',
              show_default=True)
@click.option('--part_number_list', type=str,
              help='''partNumberList query parameter.''',
              show_default=True)
@click.option('--operational_state_code_list', type=str,
              help='''operationalStateCodeList query parameter.''',
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
def get_module_count(obj, pretty_print, beep,
                     device_id,
                     name_list,
                     vendor_equipment_type_list,
                     part_number_list,
                     operational_state_code_list,
                     headers,
                     payload,
                     active_validation):
    """Returns Module Count.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_module_count(
            device_id=device_id,
            name_list=name_list,
            vendor_equipment_type_list=vendor_equipment_type_list,
            part_number_list=part_number_list,
            operational_state_code_list=operational_state_code_list,
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


@devices.command()
@click.option('--device_id', type=str,
              help='''Device ID.''',
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
def get_device_interface_count_by_id(obj, pretty_print, beep,
                                     device_id,
                                     headers,
                                     payload,
                                     active_validation):
    """Returns the interface count for the given device.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_interface_count_by_id(
            device_id=device_id,
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


@devices.command()
@click.option('--id', type=str,
              help='''Device ID.''',
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
def get_organization_list_for_meraki(obj, pretty_print, beep,
                                     id,
                                     headers,
                                     payload,
                                     active_validation):
    """Returns list of organizations for meraki dashboard.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_organization_list_for_meraki(
            id=id,
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


@devices.command()
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
def get_ospf_interfaces(obj, pretty_print, beep,
                        headers,
                        payload,
                        active_validation):
    """Returns the interfaces that has OSPF enabled.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_ospf_interfaces(
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


@devices.command()
@click.option('--id', type=str,
              help='''Functional Capability UUID.''',
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
def get_functional_capability_by_id(obj, pretty_print, beep,
                                    id,
                                    headers,
                                    payload,
                                    active_validation):
    """Returns functional capability with given Id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_functional_capability_by_id(
            id=id,
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


@devices.command()
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
def get_isis_interfaces(obj, pretty_print, beep,
                        headers,
                        payload,
                        active_validation):
    """Returns the interfaces that has ISIS enabled.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_isis_interfaces(
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


@devices.command()
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
def get_device_config_for_all_devices(obj, pretty_print, beep,
                                      headers,
                                      payload,
                                      active_validation):
    """Returns the config for all devices.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_config_for_all_devices(
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


@devices.command()
@click.option('--id', type=str,
              help='''NetworkDeviceBriefNIO's id.''',
              default=None,
              show_default=True)
@click.option('--role', type=str,
              help='''NetworkDeviceBriefNIO's role.''',
              default=None,
              show_default=True)
@click.option('--rolesource', type=str,
              help='''NetworkDeviceBriefNIO's roleSource.''',
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
def update_device_role(obj, pretty_print, beep,
                       id,
                       role,
                       rolesource,
                       headers,
                       payload,
                       active_validation):
    """Updates the role of the device as access, core, distribution, border router.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.update_device_role(
            id=id,
            role=role,
            roleSource=rolesource,
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


@devices.command()
@click.option('--device_id', type=str,
              help='''Device ID.''',
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
def get_interface_info_by_id(obj, pretty_print, beep,
                             device_id,
                             headers,
                             payload,
                             active_validation):
    """Returns list of interfaces by specified device.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_interface_info_by_id(
            device_id=device_id,
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


@devices.command()
@click.option('--ip_address', type=str,
              help='''IP address of the interface.''',
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
def get_interface_by_ip(obj, pretty_print, beep,
                        ip_address,
                        headers,
                        payload,
                        active_validation):
    """Returns list of interfaces by specified IP address.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_interface_by_ip(
            ip_address=ip_address,
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


@devices.command()
@click.option('--ip_address', type=str,
              help='''Device IP address.''',
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
def get_network_device_by_ip(obj, pretty_print, beep,
                             ip_address,
                             headers,
                             payload,
                             active_validation):
    """Returns the network device by specified IP address.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_network_device_by_ip(
            ip_address=ip_address,
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


@devices.command()
@click.option('--id', type=str,
              help='''Device ID.''',
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
def get_device_summary(obj, pretty_print, beep,
                       id,
                       headers,
                       payload,
                       active_validation):
    """Returns brief summary of device info such as hostname, management IP address for the given device Id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_summary(
            id=id,
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


@devices.command()
@click.option('--id', type=str,
              help='''Device ID.''',
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
def get_device_by_id(obj, pretty_print, beep,
                     id,
                     headers,
                     payload,
                     active_validation):
    """Returns the network device details for the given device ID.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_by_id(
            id=id,
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


@devices.command()
@click.option('--offset', type=int,
              help='''offset query parameter.''',
              show_default=True)
@click.option('--limit', type=int,
              help='''limit query parameter.''',
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
def get_all_interfaces(obj, pretty_print, beep,
                       offset,
                       limit,
                       headers,
                       payload,
                       active_validation):
    """Returns all available interfaces. This endpoint can return a maximum of 500 interfaces.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_all_interfaces(
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


@devices.command()
@click.option('--clitransport', type=str,
              help='''InventoryDeviceInfo's cliTransport.''',
              default=None,
              show_default=True)
@click.option('--computedevice', type=bool,
              help='''InventoryDeviceInfo's computeDevice.''',
              default=None,
              show_default=True)
@click.option('--enablepassword', type=str,
              help='''InventoryDeviceInfo's enablePassword.''',
              default=None,
              show_default=True)
@click.option('--extendeddiscoveryinfo', type=str,
              help='''InventoryDeviceInfo's extendedDiscoveryInfo.''',
              default=None,
              show_default=True)
@click.option('--httppassword', type=str,
              help='''InventoryDeviceInfo's httpPassword.''',
              default=None,
              show_default=True)
@click.option('--httpport', type=str,
              help='''InventoryDeviceInfo's httpPort.''',
              default=None,
              show_default=True)
@click.option('--httpsecure', type=bool,
              help='''InventoryDeviceInfo's httpSecure.''',
              default=None,
              show_default=True)
@click.option('--httpusername', type=str,
              help='''InventoryDeviceInfo's httpUserName.''',
              default=None,
              show_default=True)
@click.option('--ipaddress', type=str, multiple=True,
              help='''InventoryDeviceInfo's ipAddress (list of strings).''',
              default=None,
              show_default=True)
@click.option('--merakiorgid', type=str, multiple=True,
              help='''InventoryDeviceInfo's merakiOrgId (list of strings).''',
              default=None,
              show_default=True)
@click.option('--netconfport', type=str,
              help='''InventoryDeviceInfo's netconfPort.''',
              default=None,
              show_default=True)
@click.option('--password', type=str,
              help='''InventoryDeviceInfo's password.''',
              default=None,
              show_default=True)
@click.option('--serialnumber', type=str,
              help='''InventoryDeviceInfo's serialNumber.''',
              default=None,
              show_default=True)
@click.option('--snmpauthpassphrase', type=str,
              help='''InventoryDeviceInfo's snmpAuthPassphrase.''',
              default=None,
              show_default=True)
@click.option('--snmpauthprotocol', type=str,
              help='''InventoryDeviceInfo's snmpAuthProtocol.''',
              default=None,
              show_default=True)
@click.option('--snmpmode', type=str,
              help='''InventoryDeviceInfo's snmpMode.''',
              default=None,
              show_default=True)
@click.option('--snmpprivpassphrase', type=str,
              help='''InventoryDeviceInfo's snmpPrivPassphrase.''',
              default=None,
              show_default=True)
@click.option('--snmpprivprotocol', type=str,
              help='''InventoryDeviceInfo's snmpPrivProtocol.''',
              default=None,
              show_default=True)
@click.option('--snmprocommunity', type=str,
              help='''InventoryDeviceInfo's snmpROCommunity.''',
              default=None,
              show_default=True)
@click.option('--snmprwcommunity', type=str,
              help='''InventoryDeviceInfo's snmpRWCommunity.''',
              default=None,
              show_default=True)
@click.option('--snmpretry', type=int,
              help='''InventoryDeviceInfo's snmpRetry.''',
              default=None,
              show_default=True)
@click.option('--snmptimeout', type=int,
              help='''InventoryDeviceInfo's snmpTimeout.''',
              default=None,
              show_default=True)
@click.option('--snmpusername', type=str,
              help='''InventoryDeviceInfo's snmpUserName.''',
              default=None,
              show_default=True)
@click.option('--snmpversion', type=str,
              help='''InventoryDeviceInfo's snmpVersion.''',
              default=None,
              show_default=True)
@click.option('--type', type=str,
              help='''InventoryDeviceInfo's type. Available values are 'COMPUTE_DEVICE', 'MERAKI_DASHBOARD', 'NETWORK_DEVICE' and 'NODATACHANGE'.''',
              default=None,
              show_default=True)
@click.option('--updatemgmtipaddresslist', type=str, multiple=True,
              help='''InventoryDeviceInfo's updateMgmtIPaddressList (list of objects).''',
              default=None,
              show_default=True)
@click.option('--username', type=str,
              help='''InventoryDeviceInfo's userName.''',
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
def sync_devices(obj, pretty_print, beep,
                 clitransport,
                 computedevice,
                 enablepassword,
                 extendeddiscoveryinfo,
                 httppassword,
                 httpport,
                 httpsecure,
                 httpusername,
                 ipaddress,
                 merakiorgid,
                 netconfport,
                 password,
                 serialnumber,
                 snmpauthpassphrase,
                 snmpauthprotocol,
                 snmpmode,
                 snmpprivpassphrase,
                 snmpprivprotocol,
                 snmprocommunity,
                 snmprwcommunity,
                 snmpretry,
                 snmptimeout,
                 snmpusername,
                 snmpversion,
                 type,
                 updatemgmtipaddresslist,
                 username,
                 headers,
                 payload,
                 active_validation):
    """Sync the devices provided as input.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        ipaddress = list(ipaddress)
        ipaddress = ipaddress if len(ipaddress) > 0 else None
        merakiorgid = list(merakiorgid)
        merakiorgid = merakiorgid if len(merakiorgid) > 0 else None
        updatemgmtipaddresslist = list(updatemgmtipaddresslist)
        updatemgmtipaddresslist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in updatemgmtipaddresslist)))
        updatemgmtipaddresslist = updatemgmtipaddresslist if len(updatemgmtipaddresslist) > 0 else None
        result = obj.sync_devices(
            cliTransport=clitransport,
            computeDevice=computedevice,
            enablePassword=enablepassword,
            extendedDiscoveryInfo=extendeddiscoveryinfo,
            httpPassword=httppassword,
            httpPort=httpport,
            httpSecure=httpsecure,
            httpUserName=httpusername,
            ipAddress=ipaddress,
            merakiOrgId=merakiorgid,
            netconfPort=netconfport,
            password=password,
            serialNumber=serialnumber,
            snmpAuthPassphrase=snmpauthpassphrase,
            snmpAuthProtocol=snmpauthprotocol,
            snmpMode=snmpmode,
            snmpPrivPassphrase=snmpprivpassphrase,
            snmpPrivProtocol=snmpprivprotocol,
            snmpROCommunity=snmprocommunity,
            snmpRWCommunity=snmprwcommunity,
            snmpRetry=snmpretry,
            snmpTimeout=snmptimeout,
            snmpUserName=snmpusername,
            snmpVersion=snmpversion,
            type=type,
            updateMgmtIPaddressList=updatemgmtipaddresslist,
            userName=username,
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


@devices.command()
@click.option('--id', type=str,
              help='''Interface ID.''',
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
def get_interface_by_id(obj, pretty_print, beep,
                        id,
                        headers,
                        payload,
                        active_validation):
    """Returns the interface for the given interface ID.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_interface_by_id(
            id=id,
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


@devices.command()
@click.option('--device_id', type=str,
              help='''Accepts comma separated deviceid's and return list of functional-capabilities for the given id's. If invalid or not-found id's are provided, null entry will be returned in the list.''',
              required=True,
              show_default=True)
@click.option('--function_name', type=str,
              help='''functionName query parameter.''',
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
def get_functional_capability_for_devices(obj, pretty_print, beep,
                                          device_id,
                                          function_name,
                                          headers,
                                          payload,
                                          active_validation):
    """Returns the functional-capability for given devices.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_functional_capability_for_devices(
            device_id=device_id,
            function_name=function_name,
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


@devices.command()
@click.option('--serial_number', type=str,
              help='''Serial number of the device.''',
              show_default=True)
@click.option('--macaddress', type=str,
              help='''Mac addres of the device.''',
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
def register_device_for_wsa(obj, pretty_print, beep,
                            serial_number,
                            macaddress,
                            headers,
                            payload,
                            active_validation):
    """Registers a device for WSA notification.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.register_device_for_wsa(
            serial_number=serial_number,
            macaddress=macaddress,
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


@devices.command()
@click.option('--serial_number', type=str,
              help='''Device serial number.''',
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
def get_device_by_serial_number(obj, pretty_print, beep,
                                serial_number,
                                headers,
                                payload,
                                active_validation):
    """Returns the network device with given serial number.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_by_serial_number(
            serial_number=serial_number,
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


@devices.command()
@click.option('--deviceuuids', type=str, multiple=True,
              help='''ExportDeviceDTO's deviceUuids (list of strings).''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''ExportDeviceDTO's id.''',
              default=None,
              show_default=True)
@click.option('--operationenum', type=str,
              help='''ExportDeviceDTO's operationEnum. Available values are 'CREDENTIALDETAILS' and 'DEVICEDETAILS'.''',
              default=None,
              show_default=True)
@click.option('--parameters', type=str, multiple=True,
              help='''ExportDeviceDTO's parameters (list of strings).''',
              default=None,
              show_default=True)
@click.option('--password', type=str,
              help='''ExportDeviceDTO's password.''',
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
def export_device_list(obj, pretty_print, beep,
                       deviceuuids,
                       id,
                       operationenum,
                       parameters,
                       password,
                       headers,
                       payload,
                       active_validation):
    """Exports the selected network device to a file.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        deviceuuids = list(deviceuuids)
        deviceuuids = deviceuuids if len(deviceuuids) > 0 else None
        parameters = list(parameters)
        parameters = parameters if len(parameters) > 0 else None
        result = obj.export_device_list(
            deviceUuids=deviceuuids,
            id=id,
            operationEnum=operationenum,
            parameters=parameters,
            password=password,
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


@devices.command()
@click.option('--start_index', type=int,
              help='''Start index.''',
              required=True,
              show_default=True)
@click.option('--records_to_return', type=int,
              help='''Number of records to return.''',
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
def get_network_device_by_pagination_range(obj, pretty_print, beep,
                                           start_index,
                                           records_to_return,
                                           headers,
                                           payload,
                                           active_validation):
    """Returns the list of network devices for the given pagination range.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_network_device_by_pagination_range(
            start_index=start_index,
            records_to_return=records_to_return,
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


@devices.command()
@click.option('--vrf_name', type=str,
              help='''vrfName query parameter.''',
              show_default=True)
@click.option('--management_ip_address', type=str,
              help='''managementIpAddress query parameter.''',
              show_default=True)
@click.option('--hostname', type=str,
              help='''hostname query parameter.''',
              show_default=True)
@click.option('--mac_address', type=str,
              help='''macAddress query parameter.''',
              show_default=True)
@click.option('--family', type=str,
              help='''family query parameter.''',
              show_default=True)
@click.option('--collection_status', type=str,
              help='''collectionStatus query parameter.''',
              show_default=True)
@click.option('--collection_interval', type=str,
              help='''collectionInterval query parameter.''',
              show_default=True)
@click.option('--software_version', type=str,
              help='''softwareVersion query parameter.''',
              show_default=True)
@click.option('--software_type', type=str,
              help='''softwareType query parameter.''',
              show_default=True)
@click.option('--reachability_status', type=str,
              help='''reachabilityStatus query parameter.''',
              show_default=True)
@click.option('--reachability_failure_reason', type=str,
              help='''reachabilityFailureReason query parameter.''',
              show_default=True)
@click.option('--error_code', type=str,
              help='''errorCode query parameter.''',
              show_default=True)
@click.option('--platform_id', type=str,
              help='''platformId query parameter.''',
              show_default=True)
@click.option('--series', type=str,
              help='''series query parameter.''',
              show_default=True)
@click.option('--type', type=str,
              help='''type query parameter.''',
              show_default=True)
@click.option('--serial_number', type=str,
              help='''serialNumber query parameter.''',
              show_default=True)
@click.option('--up_time', type=str,
              help='''upTime query parameter.''',
              show_default=True)
@click.option('--role', type=str,
              help='''role query parameter.''',
              show_default=True)
@click.option('--role_source', type=str,
              help='''roleSource query parameter.''',
              show_default=True)
@click.option('--associated_wlc_ip', type=str,
              help='''associatedWlcIp query parameter.''',
              show_default=True)
@click.option('--offset', type=str,
              help='''offset query parameter.''',
              show_default=True)
@click.option('--limit', type=str,
              help='''limit query parameter.''',
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
def retrieves_all_network_devices(obj, pretty_print, beep,
                                  vrf_name,
                                  management_ip_address,
                                  hostname,
                                  mac_address,
                                  family,
                                  collection_status,
                                  collection_interval,
                                  software_version,
                                  software_type,
                                  reachability_status,
                                  reachability_failure_reason,
                                  error_code,
                                  platform_id,
                                  series,
                                  type,
                                  serial_number,
                                  up_time,
                                  role,
                                  role_source,
                                  associated_wlc_ip,
                                  offset,
                                  limit,
                                  headers,
                                  payload,
                                  active_validation):
    """Gets the list of first 500 network devices sorted lexicographically based on host name. It can be filtered using management IP address, mac address, hostname and location name. If id param is provided, it will be returning the list of network-devices for the given id's and other request params will be ignored. In case of autocomplete request, returns the list of specified attributes.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.retrieves_all_network_devices(
            vrf_name=vrf_name,
            management_ip_address=management_ip_address,
            hostname=hostname,
            mac_address=mac_address,
            family=family,
            collection_status=collection_status,
            collection_interval=collection_interval,
            software_version=software_version,
            software_type=software_type,
            reachability_status=reachability_status,
            reachability_failure_reason=reachability_failure_reason,
            error_code=error_code,
            platform_id=platform_id,
            series=series,
            type=type,
            serial_number=serial_number,
            up_time=up_time,
            role=role,
            role_source=role_source,
            associated_wlc_ip=associated_wlc_ip,
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


@devices.command()
@click.option('--device_id', type=str,
              help='''deviceId query parameter.''',
              required=True,
              show_default=True)
@click.option('--limit', type=str,
              help='''limit query parameter.''',
              show_default=True)
@click.option('--offset', type=str,
              help='''offset query parameter.''',
              show_default=True)
@click.option('--name_list', type=str,
              help='''nameList query parameter.''',
              show_default=True)
@click.option('--vendor_equipment_type_list', type=str,
              help='''vendorEquipmentTypeList query parameter.''',
              show_default=True)
@click.option('--part_number_list', type=str,
              help='''partNumberList query parameter.''',
              show_default=True)
@click.option('--operational_state_code_list', type=str,
              help='''operationalStateCodeList query parameter.''',
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
def get_modules(obj, pretty_print, beep,
                device_id,
                limit,
                offset,
                name_list,
                vendor_equipment_type_list,
                part_number_list,
                operational_state_code_list,
                headers,
                payload,
                active_validation):
    """Returns modules by specified device id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_modules(
            device_id=device_id,
            limit=limit,
            offset=offset,
            name_list=name_list,
            vendor_equipment_type_list=vendor_equipment_type_list,
            part_number_list=part_number_list,
            operational_state_code_list=operational_state_code_list,
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


@devices.command()
@click.option('--id', type=str,
              help='''Device ID.''',
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
def get_wireless_lan_controller_details_by_id(obj, pretty_print, beep,
                                              id,
                                              headers,
                                              payload,
                                              active_validation):
    """Returns the wireless lan controller info with given device ID.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_wireless_lan_controller_details_by_id(
            id=id,
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


@devices.command()
@click.option('--timestamp', type=str,
              help='''Epoch time(in milliseconds) when the device data is required.''',
              show_default=True)
@click.option('--search_by', type=str,
              help='''MAC Address or Device Name value or UUID of the network device.''',
              required=True,
              show_default=True)
@click.option('--identifier', type=str,
              help='''One of keywords macAddress or uuid or nwDeviceName.''',
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
def get_device_detail(obj, pretty_print, beep,
                      timestamp,
                      search_by,
                      identifier,
                      headers,
                      payload,
                      active_validation):
    """Returns detailed Network Device information retrieved by Mac Address, Device Name or UUID for any given point of time. .
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_detail(
            timestamp=timestamp,
            search_by=search_by,
            identifier=identifier,
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
