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
def network_discovery(ctx, obj):
    """DNA Center Network Discovery API (version: 1.2.10).

    Wraps the DNA Center Network Discovery API and exposes the API as native Python commands.

    """
    ctx.obj = obj.network_discovery


@network_discovery.command()
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
def get_count_of_all_discovery_jobs(obj, pretty_print, beep,
                                    headers,
                                    payload,
                                    active_validation):
    """Returns the count of all available discovery jobs.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_count_of_all_discovery_jobs(
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


@network_discovery.command()
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
def create_netconf_credentials(obj, pretty_print, beep,
                               headers,
                               payload,
                               active_validation):
    """Adds global netconf credentials.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.create_netconf_credentials(
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


@network_discovery.command()
@click.option('--comments', type=str,
              help='''SNMPv2WriteCommunityDTO's comments.''',
              default=None,
              show_default=True)
@click.option('--credentialtype', type=str,
              help='''SNMPv2WriteCommunityDTO's credentialType. Available values are 'GLOBAL' and 'APP'.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''SNMPv2WriteCommunityDTO's description.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''SNMPv2WriteCommunityDTO's id.''',
              default=None,
              show_default=True)
@click.option('--instancetenantid', type=str,
              help='''SNMPv2WriteCommunityDTO's instanceTenantId.''',
              default=None,
              show_default=True)
@click.option('--instanceuuid', type=str,
              help='''SNMPv2WriteCommunityDTO's instanceUuid.''',
              default=None,
              show_default=True)
@click.option('--writecommunity', type=str,
              help='''SNMPv2WriteCommunityDTO's writeCommunity.''',
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
def update_snmp_write_community(obj, pretty_print, beep,
                                comments,
                                credentialtype,
                                description,
                                id,
                                instancetenantid,
                                instanceuuid,
                                writecommunity,
                                headers,
                                payload,
                                active_validation):
    """Updates global SNMP write community.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.update_snmp_write_community(
            comments=comments,
            credentialType=credentialtype,
            description=description,
            id=id,
            instanceTenantId=instancetenantid,
            instanceUuid=instanceuuid,
            writeCommunity=writecommunity,
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


@network_discovery.command()
@click.option('--authpassword', type=str,
              help='''SNMPv3CredentialDTO's authPassword.''',
              default=None,
              show_default=True)
@click.option('--authtype', type=str,
              help='''SNMPv3CredentialDTO's authType. Available values are 'SHA' and 'MD5'.''',
              default=None,
              show_default=True)
@click.option('--comments', type=str,
              help='''SNMPv3CredentialDTO's comments.''',
              default=None,
              show_default=True)
@click.option('--credentialtype', type=str,
              help='''SNMPv3CredentialDTO's credentialType. Available values are 'GLOBAL' and 'APP'.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''SNMPv3CredentialDTO's description.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''SNMPv3CredentialDTO's id.''',
              default=None,
              show_default=True)
@click.option('--instancetenantid', type=str,
              help='''SNMPv3CredentialDTO's instanceTenantId.''',
              default=None,
              show_default=True)
@click.option('--instanceuuid', type=str,
              help='''SNMPv3CredentialDTO's instanceUuid.''',
              default=None,
              show_default=True)
@click.option('--privacypassword', type=str,
              help='''SNMPv3CredentialDTO's privacyPassword.''',
              default=None,
              show_default=True)
@click.option('--privacytype', type=str,
              help='''SNMPv3CredentialDTO's privacyType. Available values are 'DES' and 'AES128'.''',
              default=None,
              show_default=True)
@click.option('--snmpmode', type=str,
              help='''SNMPv3CredentialDTO's snmpMode. Available values are 'AUTHPRIV', 'AUTHNOPRIV' and 'NOAUTHNOPRIV'.''',
              default=None,
              show_default=True)
@click.option('--username', type=str,
              help='''SNMPv3CredentialDTO's username.''',
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
def update_snmpv3_credentials(obj, pretty_print, beep,
                              authpassword,
                              authtype,
                              comments,
                              credentialtype,
                              description,
                              id,
                              instancetenantid,
                              instanceuuid,
                              privacypassword,
                              privacytype,
                              snmpmode,
                              username,
                              headers,
                              payload,
                              active_validation):
    """Updates global SNMPv3 credential.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.update_snmpv3_credentials(
            authPassword=authpassword,
            authType=authtype,
            comments=comments,
            credentialType=credentialtype,
            description=description,
            id=id,
            instanceTenantId=instancetenantid,
            instanceUuid=instanceuuid,
            privacyPassword=privacypassword,
            privacyType=privacytype,
            snmpMode=snmpmode,
            username=username,
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


@network_discovery.command()
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
def get_snmp_properties(obj, pretty_print, beep,
                        headers,
                        payload,
                        active_validation):
    """Returns SNMP properties.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_snmp_properties(
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


@network_discovery.command()
@click.option('--id', type=str,
              help='''Discovery ID.''',
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
def delete_discovery_by_id(obj, pretty_print, beep,
                           id,
                           headers,
                           payload,
                           active_validation):
    """Stops the discovery for the given Discovery ID and removes it. Discovery ID can be obtained using the "Get Discoveries by range" API.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.delete_discovery_by_id(
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


@network_discovery.command()
@click.option('--cdplevel', type=int,
              help='''InventoryRequest's cdpLevel.''',
              default=None,
              show_default=True)
@click.option('--discoverytype', type=str,
              help='''InventoryRequest's discoveryType.''',
              default=None,
              show_default=True)
@click.option('--enablepasswordlist', type=str, multiple=True,
              help='''InventoryRequest's enablePasswordList (list of string, objects).''',
              default=None,
              show_default=True)
@click.option('--globalcredentialidlist', type=str, multiple=True,
              help='''InventoryRequest's globalCredentialIdList (list of string, objects).''',
              default=None,
              show_default=True)
@click.option('--httpreadcredential', type=str,
              help='''InventoryRequest's httpReadCredential.''',
              default=None,
              show_default=True)
@click.option('--httpwritecredential', type=str,
              help='''InventoryRequest's httpWriteCredential.''',
              default=None,
              show_default=True)
@click.option('--ipaddresslist', type=str,
              help='''InventoryRequest's ipAddressList.''',
              default=None,
              show_default=True)
@click.option('--ipfilterlist', type=str, multiple=True,
              help='''InventoryRequest's ipFilterList (list of string, objects).''',
              default=None,
              show_default=True)
@click.option('--lldplevel', type=int,
              help='''InventoryRequest's lldpLevel.''',
              default=None,
              show_default=True)
@click.option('--name', type=str,
              help='''InventoryRequest's name.''',
              default=None,
              show_default=True)
@click.option('--netconfport', type=str,
              help='''InventoryRequest's netconfPort.''',
              default=None,
              show_default=True)
@click.option('--noaddnewdevice', type=bool,
              help='''InventoryRequest's noAddNewDevice.''',
              default=None,
              show_default=True)
@click.option('--parentdiscoveryid', type=str,
              help='''InventoryRequest's parentDiscoveryId.''',
              default=None,
              show_default=True)
@click.option('--passwordlist', type=str, multiple=True,
              help='''InventoryRequest's passwordList (list of string, objects).''',
              default=None,
              show_default=True)
@click.option('--preferredmgmtipmethod', type=str,
              help='''InventoryRequest's preferredMgmtIPMethod.''',
              default=None,
              show_default=True)
@click.option('--protocolorder', type=str,
              help='''InventoryRequest's protocolOrder.''',
              default=None,
              show_default=True)
@click.option('--rediscovery', type=bool,
              help='''InventoryRequest's reDiscovery.''',
              default=None,
              show_default=True)
@click.option('--retry', type=int,
              help='''InventoryRequest's retry.''',
              default=None,
              show_default=True)
@click.option('--snmpauthpassphrase', type=str,
              help='''InventoryRequest's snmpAuthPassphrase.''',
              default=None,
              show_default=True)
@click.option('--snmpauthprotocol', type=str,
              help='''InventoryRequest's snmpAuthProtocol.''',
              default=None,
              show_default=True)
@click.option('--snmpmode', type=str,
              help='''InventoryRequest's snmpMode.''',
              default=None,
              show_default=True)
@click.option('--snmpprivpassphrase', type=str,
              help='''InventoryRequest's snmpPrivPassphrase.''',
              default=None,
              show_default=True)
@click.option('--snmpprivprotocol', type=str,
              help='''InventoryRequest's snmpPrivProtocol.''',
              default=None,
              show_default=True)
@click.option('--snmprocommunity', type=str,
              help='''InventoryRequest's snmpROCommunity.''',
              default=None,
              show_default=True)
@click.option('--snmprocommunitydesc', type=str,
              help='''InventoryRequest's snmpROCommunityDesc.''',
              default=None,
              show_default=True)
@click.option('--snmprwcommunity', type=str,
              help='''InventoryRequest's snmpRWCommunity.''',
              default=None,
              show_default=True)
@click.option('--snmprwcommunitydesc', type=str,
              help='''InventoryRequest's snmpRWCommunityDesc.''',
              default=None,
              show_default=True)
@click.option('--snmpusername', type=str,
              help='''InventoryRequest's snmpUserName.''',
              default=None,
              show_default=True)
@click.option('--snmpversion', type=str,
              help='''InventoryRequest's snmpVersion.''',
              default=None,
              show_default=True)
@click.option('--timeout', type=int,
              help='''InventoryRequest's timeout.''',
              default=None,
              show_default=True)
@click.option('--updatemgmtip', type=bool,
              help='''InventoryRequest's updateMgmtIp.''',
              default=None,
              show_default=True)
@click.option('--usernamelist', type=str, multiple=True,
              help='''InventoryRequest's userNameList (list of string, objects).''',
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
def start_discovery(obj, pretty_print, beep,
                    cdplevel,
                    discoverytype,
                    enablepasswordlist,
                    globalcredentialidlist,
                    httpreadcredential,
                    httpwritecredential,
                    ipaddresslist,
                    ipfilterlist,
                    lldplevel,
                    name,
                    netconfport,
                    noaddnewdevice,
                    parentdiscoveryid,
                    passwordlist,
                    preferredmgmtipmethod,
                    protocolorder,
                    rediscovery,
                    retry,
                    snmpauthpassphrase,
                    snmpauthprotocol,
                    snmpmode,
                    snmpprivpassphrase,
                    snmpprivprotocol,
                    snmprocommunity,
                    snmprocommunitydesc,
                    snmprwcommunity,
                    snmprwcommunitydesc,
                    snmpusername,
                    snmpversion,
                    timeout,
                    updatemgmtip,
                    usernamelist,
                    headers,
                    payload,
                    active_validation):
    """Initiates discovery with the given parameters.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        enablepasswordlist = list(enablepasswordlist)
        enablepasswordlist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in enablepasswordlist)))
        enablepasswordlist = enablepasswordlist if len(enablepasswordlist) > 0 else None
        globalcredentialidlist = list(globalcredentialidlist)
        globalcredentialidlist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in globalcredentialidlist)))
        globalcredentialidlist = globalcredentialidlist if len(globalcredentialidlist) > 0 else None
        if httpreadcredential is not None:
            httpreadcredential = json.loads('{}'.format(httpreadcredential))
        if httpwritecredential is not None:
            httpwritecredential = json.loads('{}'.format(httpwritecredential))
        ipfilterlist = list(ipfilterlist)
        ipfilterlist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in ipfilterlist)))
        ipfilterlist = ipfilterlist if len(ipfilterlist) > 0 else None
        passwordlist = list(passwordlist)
        passwordlist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in passwordlist)))
        passwordlist = passwordlist if len(passwordlist) > 0 else None
        usernamelist = list(usernamelist)
        usernamelist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in usernamelist)))
        usernamelist = usernamelist if len(usernamelist) > 0 else None
        result = obj.start_discovery(
            cdpLevel=cdplevel,
            discoveryType=discoverytype,
            enablePasswordList=enablepasswordlist,
            globalCredentialIdList=globalcredentialidlist,
            httpReadCredential=httpreadcredential,
            httpWriteCredential=httpwritecredential,
            ipAddressList=ipaddresslist,
            ipFilterList=ipfilterlist,
            lldpLevel=lldplevel,
            name=name,
            netconfPort=netconfport,
            noAddNewDevice=noaddnewdevice,
            parentDiscoveryId=parentdiscoveryid,
            passwordList=passwordlist,
            preferredMgmtIPMethod=preferredmgmtipmethod,
            protocolOrder=protocolorder,
            reDiscovery=rediscovery,
            retry=retry,
            snmpAuthPassphrase=snmpauthpassphrase,
            snmpAuthProtocol=snmpauthprotocol,
            snmpMode=snmpmode,
            snmpPrivPassphrase=snmpprivpassphrase,
            snmpPrivProtocol=snmpprivprotocol,
            snmpROCommunity=snmprocommunity,
            snmpROCommunityDesc=snmprocommunitydesc,
            snmpRWCommunity=snmprwcommunity,
            snmpRWCommunityDesc=snmprwcommunitydesc,
            snmpUserName=snmpusername,
            snmpVersion=snmpversion,
            timeout=timeout,
            updateMgmtIp=updatemgmtip,
            userNameList=usernamelist,
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


@network_discovery.command()
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
def create_snmp_write_community(obj, pretty_print, beep,
                                headers,
                                payload,
                                active_validation):
    """Adds global SNMP write community.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.create_snmp_write_community(
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


@network_discovery.command()
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
def create_http_write_credentials(obj, pretty_print, beep,
                                  headers,
                                  payload,
                                  active_validation):
    """Adds global HTTP write credentials.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.create_http_write_credentials(
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


@network_discovery.command()
@click.option('--task_id', type=str,
              help='''taskId query parameter.''',
              show_default=True)
@click.option('--sort_by', type=str,
              help='''sortBy query parameter.''',
              show_default=True)
@click.option('--sort_order', type=str,
              help='''sortOrder query parameter.''',
              show_default=True)
@click.option('--ip_address', type=str,
              help='''ipAddress query parameter.''',
              show_default=True)
@click.option('--ping_status', type=str,
              help='''pingStatus query parameter.''',
              show_default=True)
@click.option('--snmp_status', type=str,
              help='''snmpStatus query parameter.''',
              show_default=True)
@click.option('--cli_status', type=str,
              help='''cliStatus query parameter.''',
              show_default=True)
@click.option('--netconf_status', type=str,
              help='''netconfStatus query parameter.''',
              show_default=True)
@click.option('--http_status', type=str,
              help='''httpStatus query parameter.''',
              show_default=True)
@click.option('--id', type=str,
              help='''Discovery ID.''',
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
def get_network_devices_from_discovery(obj, pretty_print, beep,
                                       task_id,
                                       sort_by,
                                       sort_order,
                                       ip_address,
                                       ping_status,
                                       snmp_status,
                                       cli_status,
                                       netconf_status,
                                       http_status,
                                       id,
                                       headers,
                                       payload,
                                       active_validation):
    """Returns the network devices from a discovery job based on given filters. Discovery ID can be obtained using the "Get Discoveries by range" API.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_network_devices_from_discovery(
            task_id=task_id,
            sort_by=sort_by,
            sort_order=sort_order,
            ip_address=ip_address,
            ping_status=ping_status,
            snmp_status=snmp_status,
            cli_status=cli_status,
            netconf_status=netconf_status,
            http_status=http_status,
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


@network_discovery.command()
@click.option('--siteuuids', type=str, multiple=True,
              help='''SitesInfoDTO's siteUuids (list of strings).''',
              default=None,
              show_default=True)
@click.option('--global_credential_id', type=str,
              help='''Global credential Uuid.''',
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
def update_global_credentials(obj, pretty_print, beep,
                              siteuuids,
                              global_credential_id,
                              headers,
                              payload,
                              active_validation):
    """Update global credential for network devices in site(s).
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        siteuuids = list(siteuuids)
        siteuuids = siteuuids if len(siteuuids) > 0 else None
        result = obj.update_global_credentials(
            siteUuids=siteuuids,
            global_credential_id=global_credential_id,
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


@network_discovery.command()
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
def get_discoveries_by_range(obj, pretty_print, beep,
                             start_index,
                             records_to_return,
                             headers,
                             payload,
                             active_validation):
    """Returns the discovery by specified range.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_discoveries_by_range(
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


@network_discovery.command()
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
def create_snmp_read_community(obj, pretty_print, beep,
                               headers,
                               payload,
                               active_validation):
    """Adds global SNMP read community.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.create_snmp_read_community(
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


@network_discovery.command()
@click.option('--id', type=str,
              help='''Discovery ID.''',
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
def get_discovery_by_id(obj, pretty_print, beep,
                        id,
                        headers,
                        payload,
                        active_validation):
    """Returns discovery by Discovery ID. Discovery ID can be obtained using the "Get Discoveries by range" API.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_discovery_by_id(
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


@network_discovery.command()
@click.option('--attributeinfo', type=str,
              help='''DiscoveryNIO's attributeInfo.''',
              default=None,
              show_default=True)
@click.option('--cdplevel', type=int,
              help='''DiscoveryNIO's cdpLevel.''',
              default=None,
              show_default=True)
@click.option('--deviceids', type=str,
              help='''DiscoveryNIO's deviceIds.''',
              default=None,
              show_default=True)
@click.option('--discoverycondition', type=str,
              help='''DiscoveryNIO's discoveryCondition.''',
              default=None,
              show_default=True)
@click.option('--discoverystatus', type=str,
              help='''DiscoveryNIO's discoveryStatus.''',
              default=None,
              show_default=True)
@click.option('--discoverytype', type=str,
              help='''DiscoveryNIO's discoveryType.''',
              default=None,
              show_default=True)
@click.option('--enablepasswordlist', type=str,
              help='''DiscoveryNIO's enablePasswordList.''',
              default=None,
              show_default=True)
@click.option('--globalcredentialidlist', type=str, multiple=True,
              help='''DiscoveryNIO's globalCredentialIdList (list of string, objects).''',
              default=None,
              show_default=True)
@click.option('--httpreadcredential', type=str,
              help='''DiscoveryNIO's httpReadCredential.''',
              default=None,
              show_default=True)
@click.option('--httpwritecredential', type=str,
              help='''DiscoveryNIO's httpWriteCredential.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''DiscoveryNIO's id.''',
              default=None,
              show_default=True)
@click.option('--ipaddresslist', type=str,
              help='''DiscoveryNIO's ipAddressList.''',
              default=None,
              show_default=True)
@click.option('--ipfilterlist', type=str,
              help='''DiscoveryNIO's ipFilterList.''',
              default=None,
              show_default=True)
@click.option('--isautocdp', type=bool,
              help='''DiscoveryNIO's isAutoCdp.''',
              default=None,
              show_default=True)
@click.option('--lldplevel', type=int,
              help='''DiscoveryNIO's lldpLevel.''',
              default=None,
              show_default=True)
@click.option('--name', type=str,
              help='''DiscoveryNIO's name.''',
              default=None,
              show_default=True)
@click.option('--netconfport', type=str,
              help='''DiscoveryNIO's netconfPort.''',
              default=None,
              show_default=True)
@click.option('--numdevices', type=int,
              help='''DiscoveryNIO's numDevices.''',
              default=None,
              show_default=True)
@click.option('--parentdiscoveryid', type=str,
              help='''DiscoveryNIO's parentDiscoveryId.''',
              default=None,
              show_default=True)
@click.option('--passwordlist', type=str,
              help='''DiscoveryNIO's passwordList.''',
              default=None,
              show_default=True)
@click.option('--preferredmgmtipmethod', type=str,
              help='''DiscoveryNIO's preferredMgmtIPMethod.''',
              default=None,
              show_default=True)
@click.option('--protocolorder', type=str,
              help='''DiscoveryNIO's protocolOrder.''',
              default=None,
              show_default=True)
@click.option('--retrycount', type=int,
              help='''DiscoveryNIO's retryCount.''',
              default=None,
              show_default=True)
@click.option('--snmpauthpassphrase', type=str,
              help='''DiscoveryNIO's snmpAuthPassphrase.''',
              default=None,
              show_default=True)
@click.option('--snmpauthprotocol', type=str,
              help='''DiscoveryNIO's snmpAuthProtocol.''',
              default=None,
              show_default=True)
@click.option('--snmpmode', type=str,
              help='''DiscoveryNIO's snmpMode.''',
              default=None,
              show_default=True)
@click.option('--snmpprivpassphrase', type=str,
              help='''DiscoveryNIO's snmpPrivPassphrase.''',
              default=None,
              show_default=True)
@click.option('--snmpprivprotocol', type=str,
              help='''DiscoveryNIO's snmpPrivProtocol.''',
              default=None,
              show_default=True)
@click.option('--snmprocommunity', type=str,
              help='''DiscoveryNIO's snmpRoCommunity.''',
              default=None,
              show_default=True)
@click.option('--snmprocommunitydesc', type=str,
              help='''DiscoveryNIO's snmpRoCommunityDesc.''',
              default=None,
              show_default=True)
@click.option('--snmprwcommunity', type=str,
              help='''DiscoveryNIO's snmpRwCommunity.''',
              default=None,
              show_default=True)
@click.option('--snmprwcommunitydesc', type=str,
              help='''DiscoveryNIO's snmpRwCommunityDesc.''',
              default=None,
              show_default=True)
@click.option('--snmpusername', type=str,
              help='''DiscoveryNIO's snmpUserName.''',
              default=None,
              show_default=True)
@click.option('--timeout', type=int,
              help='''DiscoveryNIO's timeOut.''',
              default=None,
              show_default=True)
@click.option('--updatemgmtip', type=bool,
              help='''DiscoveryNIO's updateMgmtIp.''',
              default=None,
              show_default=True)
@click.option('--usernamelist', type=str,
              help='''DiscoveryNIO's userNameList.''',
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
def updates_discovery_by_id(obj, pretty_print, beep,
                            attributeinfo,
                            cdplevel,
                            deviceids,
                            discoverycondition,
                            discoverystatus,
                            discoverytype,
                            enablepasswordlist,
                            globalcredentialidlist,
                            httpreadcredential,
                            httpwritecredential,
                            id,
                            ipaddresslist,
                            ipfilterlist,
                            isautocdp,
                            lldplevel,
                            name,
                            netconfport,
                            numdevices,
                            parentdiscoveryid,
                            passwordlist,
                            preferredmgmtipmethod,
                            protocolorder,
                            retrycount,
                            snmpauthpassphrase,
                            snmpauthprotocol,
                            snmpmode,
                            snmpprivpassphrase,
                            snmpprivprotocol,
                            snmprocommunity,
                            snmprocommunitydesc,
                            snmprwcommunity,
                            snmprwcommunitydesc,
                            snmpusername,
                            timeout,
                            updatemgmtip,
                            usernamelist,
                            headers,
                            payload,
                            active_validation):
    """Stops or starts an existing discovery.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        if attributeinfo is not None:
            attributeinfo = json.loads('{}'.format(attributeinfo))
        globalcredentialidlist = list(globalcredentialidlist)
        globalcredentialidlist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in globalcredentialidlist)))
        globalcredentialidlist = globalcredentialidlist if len(globalcredentialidlist) > 0 else None
        if httpreadcredential is not None:
            httpreadcredential = json.loads('{}'.format(httpreadcredential))
        if httpwritecredential is not None:
            httpwritecredential = json.loads('{}'.format(httpwritecredential))
        result = obj.updates_discovery_by_id(
            attributeInfo=attributeinfo,
            cdpLevel=cdplevel,
            deviceIds=deviceids,
            discoveryCondition=discoverycondition,
            discoveryStatus=discoverystatus,
            discoveryType=discoverytype,
            enablePasswordList=enablepasswordlist,
            globalCredentialIdList=globalcredentialidlist,
            httpReadCredential=httpreadcredential,
            httpWriteCredential=httpwritecredential,
            id=id,
            ipAddressList=ipaddresslist,
            ipFilterList=ipfilterlist,
            isAutoCdp=isautocdp,
            lldpLevel=lldplevel,
            name=name,
            netconfPort=netconfport,
            numDevices=numdevices,
            parentDiscoveryId=parentdiscoveryid,
            passwordList=passwordlist,
            preferredMgmtIPMethod=preferredmgmtipmethod,
            protocolOrder=protocolorder,
            retryCount=retrycount,
            snmpAuthPassphrase=snmpauthpassphrase,
            snmpAuthProtocol=snmpauthprotocol,
            snmpMode=snmpmode,
            snmpPrivPassphrase=snmpprivpassphrase,
            snmpPrivProtocol=snmpprivprotocol,
            snmpRoCommunity=snmprocommunity,
            snmpRoCommunityDesc=snmprocommunitydesc,
            snmpRwCommunity=snmprwcommunity,
            snmpRwCommunityDesc=snmprwcommunitydesc,
            snmpUserName=snmpusername,
            timeOut=timeout,
            updateMgmtIp=updatemgmtip,
            userNameList=usernamelist,
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


@network_discovery.command()
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
def create_cli_credentials(obj, pretty_print, beep,
                           headers,
                           payload,
                           active_validation):
    """Adds global CLI credential.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.create_cli_credentials(
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


@network_discovery.command()
@click.option('--comments', type=str,
              help='''SNMPv2ReadCommunityDTO's comments.''',
              default=None,
              show_default=True)
@click.option('--credentialtype', type=str,
              help='''SNMPv2ReadCommunityDTO's credentialType. Available values are 'GLOBAL' and 'APP'.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''SNMPv2ReadCommunityDTO's description.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''SNMPv2ReadCommunityDTO's id.''',
              default=None,
              show_default=True)
@click.option('--instancetenantid', type=str,
              help='''SNMPv2ReadCommunityDTO's instanceTenantId.''',
              default=None,
              show_default=True)
@click.option('--instanceuuid', type=str,
              help='''SNMPv2ReadCommunityDTO's instanceUuid.''',
              default=None,
              show_default=True)
@click.option('--readcommunity', type=str,
              help='''SNMPv2ReadCommunityDTO's readCommunity.''',
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
def update_snmp_read_community(obj, pretty_print, beep,
                               comments,
                               credentialtype,
                               description,
                               id,
                               instancetenantid,
                               instanceuuid,
                               readcommunity,
                               headers,
                               payload,
                               active_validation):
    """Updates global SNMP read community.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.update_snmp_read_community(
            comments=comments,
            credentialType=credentialtype,
            description=description,
            id=id,
            instanceTenantId=instancetenantid,
            instanceUuid=instanceuuid,
            readCommunity=readcommunity,
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


@network_discovery.command()
@click.option('--offset', type=int,
              help='''offset query parameter.''',
              show_default=True)
@click.option('--limit', type=int,
              help='''limit query parameter.''',
              show_default=True)
@click.option('--ip_address', type=str,
              help='''ipAddress query parameter.''',
              show_default=True)
@click.option('--id', type=str,
              help='''Discovery ID.''',
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
def get_list_of_discoveries_by_discovery_id(obj, pretty_print, beep,
                                            offset,
                                            limit,
                                            ip_address,
                                            id,
                                            headers,
                                            payload,
                                            active_validation):
    """Returns the list of discovery jobs for the given Discovery ID. The results can be optionally filtered based on IP. Discovery ID can be obtained using the "Get Discoveries by range" API.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_list_of_discoveries_by_discovery_id(
            offset=offset,
            limit=limit,
            ip_address=ip_address,
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


@network_discovery.command()
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
def create_update_snmp_properties(obj, pretty_print, beep,
                                  headers,
                                  payload,
                                  active_validation):
    """Adds SNMP properties.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.create_update_snmp_properties(
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


@network_discovery.command()
@click.option('--offset', type=int,
              help='''offset query parameter.''',
              show_default=True)
@click.option('--limit', type=int,
              help='''limit query parameter.''',
              show_default=True)
@click.option('--ip_address', type=str,
              help='''ipAddress query parameter.''',
              required=True,
              show_default=True)
@click.option('--name', type=str,
              help='''name query parameter.''',
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
def get_discovery_jobs_by_ip(obj, pretty_print, beep,
                             offset,
                             limit,
                             ip_address,
                             name,
                             headers,
                             payload,
                             active_validation):
    """Returns the list of discovery jobs for the given IP.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_discovery_jobs_by_ip(
            offset=offset,
            limit=limit,
            ip_address=ip_address,
            name=name,
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


@network_discovery.command()
@click.option('--task_id', type=str,
              help='''taskId query parameter.''',
              show_default=True)
@click.option('--id', type=str,
              help='''Discovery ID.''',
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
def get_discovered_devices_by_range(obj, pretty_print, beep,
                                    task_id,
                                    id,
                                    start_index,
                                    records_to_return,
                                    headers,
                                    payload,
                                    active_validation):
    """Returns the network devices discovered for the given discovery and for the given range. The maximum number of records that can be retrieved is 500. Discovery ID can be obtained using the "Get Discoveries by range" API.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_discovered_devices_by_range(
            task_id=task_id,
            id=id,
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


@network_discovery.command()
@click.option('--id', type=str,
              help='''Global Credential ID.''',
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
def get_credential_sub_type_by_credential_id(obj, pretty_print, beep,
                                             id,
                                             headers,
                                             payload,
                                             active_validation):
    """Returns the credential sub type for the given Id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_credential_sub_type_by_credential_id(
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


@network_discovery.command()
@click.option('--comments', type=str,
              help='''HTTPWriteCredentialDTO's comments.''',
              default=None,
              show_default=True)
@click.option('--credentialtype', type=str,
              help='''HTTPWriteCredentialDTO's credentialType. Available values are 'GLOBAL' and 'APP'.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''HTTPWriteCredentialDTO's description.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''HTTPWriteCredentialDTO's id.''',
              default=None,
              show_default=True)
@click.option('--instancetenantid', type=str,
              help='''HTTPWriteCredentialDTO's instanceTenantId.''',
              default=None,
              show_default=True)
@click.option('--instanceuuid', type=str,
              help='''HTTPWriteCredentialDTO's instanceUuid.''',
              default=None,
              show_default=True)
@click.option('--password', type=str,
              help='''HTTPWriteCredentialDTO's password.''',
              default=None,
              show_default=True)
@click.option('--port', type=int,
              help='''HTTPWriteCredentialDTO's port.''',
              default=None,
              show_default=True)
@click.option('--secure', type=bool,
              help='''HTTPWriteCredentialDTO's secure.''',
              default=None,
              show_default=True)
@click.option('--username', type=str,
              help='''HTTPWriteCredentialDTO's username.''',
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
def update_http_write_credentials(obj, pretty_print, beep,
                                  comments,
                                  credentialtype,
                                  description,
                                  id,
                                  instancetenantid,
                                  instanceuuid,
                                  password,
                                  port,
                                  secure,
                                  username,
                                  headers,
                                  payload,
                                  active_validation):
    """Updates global HTTP write credentials.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.update_http_write_credentials(
            comments=comments,
            credentialType=credentialtype,
            description=description,
            id=id,
            instanceTenantId=instancetenantid,
            instanceUuid=instanceuuid,
            password=password,
            port=port,
            secure=secure,
            username=username,
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


@network_discovery.command()
@click.option('--start_index', type=int,
              help='''Start index.''',
              required=True,
              show_default=True)
@click.option('--records_to_delete', type=int,
              help='''Number of records to delete.''',
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
def delete_discovery_by_specified_range(obj, pretty_print, beep,
                                        start_index,
                                        records_to_delete,
                                        headers,
                                        payload,
                                        active_validation):
    """Stops discovery for the given range and removes them.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.delete_discovery_by_specified_range(
            start_index=start_index,
            records_to_delete=records_to_delete,
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


@network_discovery.command()
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
def create_http_read_credentials(obj, pretty_print, beep,
                                 headers,
                                 payload,
                                 active_validation):
    """Adds HTTP read credentials.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.create_http_read_credentials(
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


@network_discovery.command()
@click.option('--comments', type=str,
              help='''NetconfCredentialDTO's comments.''',
              default=None,
              show_default=True)
@click.option('--credentialtype', type=str,
              help='''NetconfCredentialDTO's credentialType. Available values are 'GLOBAL' and 'APP'.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''NetconfCredentialDTO's description.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''NetconfCredentialDTO's id.''',
              default=None,
              show_default=True)
@click.option('--instancetenantid', type=str,
              help='''NetconfCredentialDTO's instanceTenantId.''',
              default=None,
              show_default=True)
@click.option('--instanceuuid', type=str,
              help='''NetconfCredentialDTO's instanceUuid.''',
              default=None,
              show_default=True)
@click.option('--netconfport', type=str,
              help='''NetconfCredentialDTO's netconfPort.''',
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
def update_netconf_credentials(obj, pretty_print, beep,
                               comments,
                               credentialtype,
                               description,
                               id,
                               instancetenantid,
                               instanceuuid,
                               netconfport,
                               headers,
                               payload,
                               active_validation):
    """Updates global netconf credentials.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.update_netconf_credentials(
            comments=comments,
            credentialType=credentialtype,
            description=description,
            id=id,
            instanceTenantId=instancetenantid,
            instanceUuid=instanceuuid,
            netconfPort=netconfport,
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


@network_discovery.command()
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
def delete_all_discovery(obj, pretty_print, beep,
                         headers,
                         payload,
                         active_validation):
    """Stops all the discoveries and removes them.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.delete_all_discovery(
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


@network_discovery.command()
@click.option('--global_credential_id', type=str,
              help='''ID of global-credential.''',
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
def delete_global_credentials_by_id(obj, pretty_print, beep,
                                    global_credential_id,
                                    headers,
                                    payload,
                                    active_validation):
    """Deletes global credential for the given ID.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.delete_global_credentials_by_id(
            global_credential_id=global_credential_id,
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


@network_discovery.command()
@click.option('--comments', type=str,
              help='''HTTPReadCredentialDTO's comments.''',
              default=None,
              show_default=True)
@click.option('--credentialtype', type=str,
              help='''HTTPReadCredentialDTO's credentialType. Available values are 'GLOBAL' and 'APP'.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''HTTPReadCredentialDTO's description.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''HTTPReadCredentialDTO's id.''',
              default=None,
              show_default=True)
@click.option('--instancetenantid', type=str,
              help='''HTTPReadCredentialDTO's instanceTenantId.''',
              default=None,
              show_default=True)
@click.option('--instanceuuid', type=str,
              help='''HTTPReadCredentialDTO's instanceUuid.''',
              default=None,
              show_default=True)
@click.option('--password', type=str,
              help='''HTTPReadCredentialDTO's password.''',
              default=None,
              show_default=True)
@click.option('--port', type=int,
              help='''HTTPReadCredentialDTO's port.''',
              default=None,
              show_default=True)
@click.option('--secure', type=bool,
              help='''HTTPReadCredentialDTO's secure.''',
              default=None,
              show_default=True)
@click.option('--username', type=str,
              help='''HTTPReadCredentialDTO's username.''',
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
def update_http_read_credential(obj, pretty_print, beep,
                                comments,
                                credentialtype,
                                description,
                                id,
                                instancetenantid,
                                instanceuuid,
                                password,
                                port,
                                secure,
                                username,
                                headers,
                                payload,
                                active_validation):
    """Updates global HTTP Read credential.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.update_http_read_credential(
            comments=comments,
            credentialType=credentialtype,
            description=description,
            id=id,
            instanceTenantId=instancetenantid,
            instanceUuid=instanceuuid,
            password=password,
            port=port,
            secure=secure,
            username=username,
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


@network_discovery.command()
@click.option('--comments', type=str,
              help='''CLICredentialDTO's comments.''',
              default=None,
              show_default=True)
@click.option('--credentialtype', type=str,
              help='''CLICredentialDTO's credentialType. Available values are 'GLOBAL' and 'APP'.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''CLICredentialDTO's description.''',
              default=None,
              show_default=True)
@click.option('--enablepassword', type=str,
              help='''CLICredentialDTO's enablePassword.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''CLICredentialDTO's id.''',
              default=None,
              show_default=True)
@click.option('--instancetenantid', type=str,
              help='''CLICredentialDTO's instanceTenantId.''',
              default=None,
              show_default=True)
@click.option('--instanceuuid', type=str,
              help='''CLICredentialDTO's instanceUuid.''',
              default=None,
              show_default=True)
@click.option('--password', type=str,
              help='''CLICredentialDTO's password.''',
              default=None,
              show_default=True)
@click.option('--username', type=str,
              help='''CLICredentialDTO's username.''',
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
def update_cli_credentials(obj, pretty_print, beep,
                           comments,
                           credentialtype,
                           description,
                           enablepassword,
                           id,
                           instancetenantid,
                           instanceuuid,
                           password,
                           username,
                           headers,
                           payload,
                           active_validation):
    """Updates global CLI credentials.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.update_cli_credentials(
            comments=comments,
            credentialType=credentialtype,
            description=description,
            enablePassword=enablepassword,
            id=id,
            instanceTenantId=instancetenantid,
            instanceUuid=instanceuuid,
            password=password,
            username=username,
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


@network_discovery.command()
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
def create_snmpv3_credentials(obj, pretty_print, beep,
                              headers,
                              payload,
                              active_validation):
    """Adds global SNMPv3 credentials.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.create_snmpv3_credentials(
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


@network_discovery.command()
@click.option('--task_id', type=str,
              help='''taskId query parameter.''',
              show_default=True)
@click.option('--id', type=str,
              help='''Discovery ID.''',
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
def get_devices_discovered_by_id(obj, pretty_print, beep,
                                 task_id,
                                 id,
                                 headers,
                                 payload,
                                 active_validation):
    """Returns the count of network devices discovered in the given discovery. Discovery ID can be obtained using the "Get Discoveries by range" API.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_devices_discovered_by_id(
            task_id=task_id,
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


@network_discovery.command()
@click.option('--task_id', type=str,
              help='''taskId query parameter.''',
              show_default=True)
@click.option('--id', type=str,
              help='''Discovery ID.''',
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
def get_discovered_network_devices_by_discovery_id(obj, pretty_print, beep,
                                                   task_id,
                                                   id,
                                                   headers,
                                                   payload,
                                                   active_validation):
    """Returns the network devices discovered for the given Discovery ID. Discovery ID can be obtained using the "Get Discoveries by range" API.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_discovered_network_devices_by_discovery_id(
            task_id=task_id,
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


@network_discovery.command()
@click.option('--credential_sub_type', type=str,
              help='''Credential type as CLI / SNMPV2_READ_COMMUNITY / SNMPV2_WRITE_COMMUNITY / SNMPV3 / HTTP_WRITE / HTTP_READ / NETCONF.''',
              required=True,
              show_default=True)
@click.option('--sort_by', type=str,
              help='''sortBy query parameter.''',
              show_default=True)
@click.option('--order', type=str,
              help='''order query parameter.''',
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
def get_global_credentials(obj, pretty_print, beep,
                           credential_sub_type,
                           sort_by,
                           order,
                           headers,
                           payload,
                           active_validation):
    """Returns global credential for the given credential sub type.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_global_credentials(
            credential_sub_type=credential_sub_type,
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
