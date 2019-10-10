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
def pnp(ctx, obj):
    """DNA Center PnP API (version: 1.2.10).

    Wraps the DNA Center PnP API and exposes the API as native Python commands.

    """
    ctx.obj = obj.pnp


@pnp.command()
@click.option('--domain', type=str,
              help='''Smart Account Domain.''',
              required=True,
              show_default=True)
@click.option('--name', type=str,
              help='''Virtual Account Name.''',
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
def get_sync_result_for_virtual_account(obj, pretty_print, beep,
                                        domain,
                                        name,
                                        headers,
                                        payload,
                                        active_validation):
    """Returns the summary of devices synced from the given smart account & virtual account with PnP.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_sync_result_for_virtual_account(
            domain=domain,
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


@pnp.command()
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
def import_devices_in_bulk(obj, pretty_print, beep,
                           headers,
                           payload,
                           active_validation):
    """Add devices to PnP in bulk.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.import_devices_in_bulk(
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


@pnp.command()
@click.option('--_id', type=str,
              help='''Workflow's _id.''',
              default=None,
              show_default=True)
@click.option('--addtoinventory', type=bool,
              help='''Workflow's addToInventory.''',
              default=None,
              show_default=True)
@click.option('--addedon', type=int,
              help='''Workflow's addedOn.''',
              default=None,
              show_default=True)
@click.option('--configid', type=str,
              help='''Workflow's configId.''',
              default=None,
              show_default=True)
@click.option('--currtaskidx', type=int,
              help='''Workflow's currTaskIdx.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''Workflow's description.''',
              default=None,
              show_default=True)
@click.option('--endtime', type=int,
              help='''Workflow's endTime.''',
              default=None,
              show_default=True)
@click.option('--exectime', type=int,
              help='''Workflow's execTime.''',
              default=None,
              show_default=True)
@click.option('--imageid', type=str,
              help='''Workflow's imageId.''',
              default=None,
              show_default=True)
@click.option('--instancetype', type=str,
              help='''Workflow's instanceType. Available values are 'SystemWorkflow', 'UserWorkflow' and 'SystemResetWorkflow'.''',
              default=None,
              show_default=True)
@click.option('--lastupdateon', type=int,
              help='''Workflow's lastupdateOn.''',
              default=None,
              show_default=True)
@click.option('--name', type=str,
              help='''Workflow's name.''',
              default=None,
              show_default=True)
@click.option('--starttime', type=int,
              help='''Workflow's startTime.''',
              default=None,
              show_default=True)
@click.option('--state', type=str,
              help='''Workflow's state.''',
              default=None,
              show_default=True)
@click.option('--tasks', type=str, multiple=True,
              help='''Workflow's tasks (list of objects).''',
              default=None,
              show_default=True)
@click.option('--tenantid', type=str,
              help='''Workflow's tenantId.''',
              default=None,
              show_default=True)
@click.option('--type', type=str,
              help='''Workflow's type.''',
              default=None,
              show_default=True)
@click.option('--usestate', type=str,
              help='''Workflow's useState.''',
              default=None,
              show_default=True)
@click.option('--version', type=int,
              help='''Workflow's version.''',
              default=None,
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
def update_workflow(obj, pretty_print, beep,
                    _id,
                    addtoinventory,
                    addedon,
                    configid,
                    currtaskidx,
                    description,
                    endtime,
                    exectime,
                    imageid,
                    instancetype,
                    lastupdateon,
                    name,
                    starttime,
                    state,
                    tasks,
                    tenantid,
                    type,
                    usestate,
                    version,
                    id,
                    headers,
                    payload,
                    active_validation):
    """Updates an existing workflow.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        tasks = list(tasks)
        tasks = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in tasks)))
        tasks = tasks if len(tasks) > 0 else None
        result = obj.update_workflow(
            _id=_id,
            addToInventory=addtoinventory,
            addedOn=addedon,
            configId=configid,
            currTaskIdx=currtaskidx,
            description=description,
            endTime=endtime,
            execTime=exectime,
            imageId=imageid,
            instanceType=instancetype,
            lastupdateOn=lastupdateon,
            name=name,
            startTime=starttime,
            state=state,
            tasks=tasks,
            tenantId=tenantid,
            type=type,
            useState=usestate,
            version=version,
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


@pnp.command()
@click.option('--deviceidlist', type=str, multiple=True,
              help='''UnclaimRequest's deviceIdList (list of string, objects).''',
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
def un_claim_device(obj, pretty_print, beep,
                    deviceidlist,
                    headers,
                    payload,
                    active_validation):
    """Un-Claims one of more devices with specified workflow.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        deviceidlist = list(deviceidlist)
        deviceidlist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in deviceidlist)))
        deviceidlist = deviceidlist if len(deviceidlist) > 0 else None
        result = obj.un_claim_device(
            deviceIdList=deviceidlist,
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


@pnp.command()
@click.option('--autosyncperiod', type=int,
              help='''SAVAMapping's autoSyncPeriod.''',
              default=None,
              show_default=True)
@click.option('--ccouser', type=str,
              help='''SAVAMapping's ccoUser.''',
              default=None,
              show_default=True)
@click.option('--expiry', type=int,
              help='''SAVAMapping's expiry.''',
              default=None,
              show_default=True)
@click.option('--lastsync', type=int,
              help='''SAVAMapping's lastSync.''',
              default=None,
              show_default=True)
@click.option('--profile', type=str,
              help='''SAVAMapping's profile.''',
              default=None,
              show_default=True)
@click.option('--smartaccountid', type=str,
              help='''SAVAMapping's smartAccountId.''',
              default=None,
              show_default=True)
@click.option('--syncresult', type=str,
              help='''SAVAMapping's syncResult.''',
              default=None,
              show_default=True)
@click.option('--syncresultstr', type=str,
              help='''SAVAMapping's syncResultStr.''',
              default=None,
              show_default=True)
@click.option('--syncstarttime', type=int,
              help='''SAVAMapping's syncStartTime.''',
              default=None,
              show_default=True)
@click.option('--syncstatus', type=str,
              help='''SAVAMapping's syncStatus. Available values are 'NOT_SYNCED', 'SYNCING', 'SUCCESS' and 'FAILURE'.''',
              default=None,
              show_default=True)
@click.option('--tenantid', type=str,
              help='''SAVAMapping's tenantId.''',
              default=None,
              show_default=True)
@click.option('--token', type=str,
              help='''SAVAMapping's token.''',
              default=None,
              show_default=True)
@click.option('--virtualaccountid', type=str,
              help='''SAVAMapping's virtualAccountId.''',
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
def add_virtual_account(obj, pretty_print, beep,
                        autosyncperiod,
                        ccouser,
                        expiry,
                        lastsync,
                        profile,
                        smartaccountid,
                        syncresult,
                        syncresultstr,
                        syncstarttime,
                        syncstatus,
                        tenantid,
                        token,
                        virtualaccountid,
                        headers,
                        payload,
                        active_validation):
    """Registers a Smart Account, Virtual Account and the relevant server profile info with the PnP System & database. The devices present in the registered virtual account are synced with the PnP database as well. The response payload returns the new profile.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        if profile is not None:
            profile = json.loads('{}'.format(profile))
        if syncresult is not None:
            syncresult = json.loads('{}'.format(syncresult))
        result = obj.add_virtual_account(
            autoSyncPeriod=autosyncperiod,
            ccoUser=ccouser,
            expiry=expiry,
            lastSync=lastsync,
            profile=profile,
            smartAccountId=smartaccountid,
            syncResult=syncresult,
            syncResultStr=syncresultstr,
            syncStartTime=syncstarttime,
            syncStatus=syncstatus,
            tenantId=tenantid,
            token=token,
            virtualAccountId=virtualaccountid,
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


@pnp.command()
@click.option('--_id', type=str,
              help='''Device's _id.''',
              default=None,
              show_default=True)
@click.option('--deviceinfo', type=str,
              help='''Device's deviceInfo.''',
              default=None,
              show_default=True)
@click.option('--runsummarylist', type=str, multiple=True,
              help='''Device's runSummaryList (list of objects).''',
              default=None,
              show_default=True)
@click.option('--systemresetworkflow', type=str,
              help='''Device's systemResetWorkflow.''',
              default=None,
              show_default=True)
@click.option('--systemworkflow', type=str,
              help='''Device's systemWorkflow.''',
              default=None,
              show_default=True)
@click.option('--tenantid', type=str,
              help='''Device's tenantId.''',
              default=None,
              show_default=True)
@click.option('--version', type=int,
              help='''Device's version.''',
              default=None,
              show_default=True)
@click.option('--workflow', type=str,
              help='''Device's workflow.''',
              default=None,
              show_default=True)
@click.option('--workflowparameters', type=str,
              help='''Device's workflowParameters.''',
              default=None,
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
def update_device(obj, pretty_print, beep,
                  _id,
                  deviceinfo,
                  runsummarylist,
                  systemresetworkflow,
                  systemworkflow,
                  tenantid,
                  version,
                  workflow,
                  workflowparameters,
                  id,
                  headers,
                  payload,
                  active_validation):
    """Updates device details specified by device id in PnP database.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        if deviceinfo is not None:
            deviceinfo = json.loads('{}'.format(deviceinfo))
        runsummarylist = list(runsummarylist)
        runsummarylist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in runsummarylist)))
        runsummarylist = runsummarylist if len(runsummarylist) > 0 else None
        if systemresetworkflow is not None:
            systemresetworkflow = json.loads('{}'.format(systemresetworkflow))
        if systemworkflow is not None:
            systemworkflow = json.loads('{}'.format(systemworkflow))
        if workflow is not None:
            workflow = json.loads('{}'.format(workflow))
        if workflowparameters is not None:
            workflowparameters = json.loads('{}'.format(workflowparameters))
        result = obj.update_device(
            _id=_id,
            deviceInfo=deviceinfo,
            runSummaryList=runsummarylist,
            systemResetWorkflow=systemresetworkflow,
            systemWorkflow=systemworkflow,
            tenantId=tenantid,
            version=version,
            workflow=workflow,
            workflowParameters=workflowparameters,
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


@pnp.command()
@click.option('--deviceid', type=str,
              help='''SiteProvisionRequest's deviceId.''',
              default=None,
              show_default=True)
@click.option('--siteid', type=str,
              help='''SiteProvisionRequest's siteId.''',
              default=None,
              show_default=True)
@click.option('--type', type=str,
              help='''SiteProvisionRequest's type. Available values are 'Default', 'AccessPoint', 'StackSwitch', 'Sensor' and 'MobilityExpress'.''',
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
def claim_a_device_to_a_site(obj, pretty_print, beep,
                             deviceid,
                             siteid,
                             type,
                             headers,
                             payload,
                             active_validation):
    """Claim a device based on DNA-C Site based design process. Different parameters are required for different device platforms.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.claim_a_device_to_a_site(
            deviceId=deviceid,
            siteId=siteid,
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


@pnp.command()
@click.option('--domain', type=str,
              help='''Smart Account Domain.''',
              required=True,
              show_default=True)
@click.option('--name', type=str,
              help='''Virtual Account Name.''',
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
def deregister_virtual_account(obj, pretty_print, beep,
                               domain,
                               name,
                               headers,
                               payload,
                               active_validation):
    """Deregisters the specified smart account & virtual account info and the associated device information from the PnP System & database. The devices associated with the deregistered virtual account are removed from the PnP database as well. The response payload contains the deregistered smart & virtual account information.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.deregister_virtual_account(
            domain=domain,
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


@pnp.command()
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
def get_smart_account_list(obj, pretty_print, beep,
                           headers,
                           payload,
                           active_validation):
    """Returns the list of Smart Account domains.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_smart_account_list(
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


@pnp.command()
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
def get_workflow_by_id(obj, pretty_print, beep,
                       id,
                       headers,
                       payload,
                       active_validation):
    """Returns a workflow specified by id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_workflow_by_id(
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


@pnp.command()
@click.option('--autosyncperiod', type=int,
              help='''SAVAMapping's autoSyncPeriod.''',
              default=None,
              show_default=True)
@click.option('--ccouser', type=str,
              help='''SAVAMapping's ccoUser.''',
              default=None,
              show_default=True)
@click.option('--expiry', type=int,
              help='''SAVAMapping's expiry.''',
              default=None,
              show_default=True)
@click.option('--lastsync', type=int,
              help='''SAVAMapping's lastSync.''',
              default=None,
              show_default=True)
@click.option('--profile', type=str,
              help='''SAVAMapping's profile.''',
              default=None,
              show_default=True)
@click.option('--smartaccountid', type=str,
              help='''SAVAMapping's smartAccountId.''',
              default=None,
              show_default=True)
@click.option('--syncresult', type=str,
              help='''SAVAMapping's syncResult.''',
              default=None,
              show_default=True)
@click.option('--syncresultstr', type=str,
              help='''SAVAMapping's syncResultStr.''',
              default=None,
              show_default=True)
@click.option('--syncstarttime', type=int,
              help='''SAVAMapping's syncStartTime.''',
              default=None,
              show_default=True)
@click.option('--syncstatus', type=str,
              help='''SAVAMapping's syncStatus. Available values are 'NOT_SYNCED', 'SYNCING', 'SUCCESS' and 'FAILURE'.''',
              default=None,
              show_default=True)
@click.option('--tenantid', type=str,
              help='''SAVAMapping's tenantId.''',
              default=None,
              show_default=True)
@click.option('--token', type=str,
              help='''SAVAMapping's token.''',
              default=None,
              show_default=True)
@click.option('--virtualaccountid', type=str,
              help='''SAVAMapping's virtualAccountId.''',
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
def update_pnp_server_profile(obj, pretty_print, beep,
                              autosyncperiod,
                              ccouser,
                              expiry,
                              lastsync,
                              profile,
                              smartaccountid,
                              syncresult,
                              syncresultstr,
                              syncstarttime,
                              syncstatus,
                              tenantid,
                              token,
                              virtualaccountid,
                              headers,
                              payload,
                              active_validation):
    """Updates the PnP Server profile in a registered Virtual Account in the PnP database. The response payload returns the updated smart & virtual account info.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        if profile is not None:
            profile = json.loads('{}'.format(profile))
        if syncresult is not None:
            syncresult = json.loads('{}'.format(syncresult))
        result = obj.update_pnp_server_profile(
            autoSyncPeriod=autosyncperiod,
            ccoUser=ccouser,
            expiry=expiry,
            lastSync=lastsync,
            profile=profile,
            smartAccountId=smartaccountid,
            syncResult=syncresult,
            syncResultStr=syncresultstr,
            syncStartTime=syncstarttime,
            syncStatus=syncstatus,
            tenantId=tenantid,
            token=token,
            virtualAccountId=virtualaccountid,
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


@pnp.command()
@click.option('--name', type=str,
              help='''Workflow Name.''',
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
def get_workflow_count(obj, pretty_print, beep,
                       name,
                       headers,
                       payload,
                       active_validation):
    """Returns the workflow count.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_workflow_count(
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


@pnp.command()
@click.option('--_id', type=str,
              help='''Settings's _id.''',
              default=None,
              show_default=True)
@click.option('--aaacredentials', type=str,
              help='''Settings's aaaCredentials.''',
              default=None,
              show_default=True)
@click.option('--accepteula', type=bool,
              help='''Settings's acceptEula.''',
              default=None,
              show_default=True)
@click.option('--defaultprofile', type=str,
              help='''Settings's defaultProfile.''',
              default=None,
              show_default=True)
@click.option('--savamappinglist', type=str, multiple=True,
              help='''Settings's savaMappingList (list of objects).''',
              default=None,
              show_default=True)
@click.option('--tasktimeouts', type=str,
              help='''Settings's taskTimeOuts.''',
              default=None,
              show_default=True)
@click.option('--tenantid', type=str,
              help='''Settings's tenantId.''',
              default=None,
              show_default=True)
@click.option('--version', type=int,
              help='''Settings's version.''',
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
def update_pnp_global_settings(obj, pretty_print, beep,
                               _id,
                               aaacredentials,
                               accepteula,
                               defaultprofile,
                               savamappinglist,
                               tasktimeouts,
                               tenantid,
                               version,
                               headers,
                               payload,
                               active_validation):
    """Updates the user's list of global PnP settings.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        if aaacredentials is not None:
            aaacredentials = json.loads('{}'.format(aaacredentials))
        if defaultprofile is not None:
            defaultprofile = json.loads('{}'.format(defaultprofile))
        savamappinglist = list(savamappinglist)
        savamappinglist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in savamappinglist)))
        savamappinglist = savamappinglist if len(savamappinglist) > 0 else None
        if tasktimeouts is not None:
            tasktimeouts = json.loads('{}'.format(tasktimeouts))
        result = obj.update_pnp_global_settings(
            _id=_id,
            aaaCredentials=aaacredentials,
            acceptEula=accepteula,
            defaultProfile=defaultprofile,
            savaMappingList=savamappinglist,
            taskTimeOuts=tasktimeouts,
            tenantId=tenantid,
            version=version,
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


@pnp.command()
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
def get_pnp_global_settings(obj, pretty_print, beep,
                            headers,
                            payload,
                            active_validation):
    """Returns global PnP settings of the user.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_pnp_global_settings(
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


@pnp.command()
@click.option('--deviceresetlist', type=str, multiple=True,
              help='''ResetRequest's deviceResetList (list of objects).''',
              default=None,
              show_default=True)
@click.option('--projectid', type=str,
              help='''ResetRequest's projectId.''',
              default=None,
              show_default=True)
@click.option('--workflowid', type=str,
              help='''ResetRequest's workflowId.''',
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
def reset_device(obj, pretty_print, beep,
                 deviceresetlist,
                 projectid,
                 workflowid,
                 headers,
                 payload,
                 active_validation):
    """Recovers a device from a Workflow Execution Error state.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        deviceresetlist = list(deviceresetlist)
        deviceresetlist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in deviceresetlist)))
        deviceresetlist = deviceresetlist if len(deviceresetlist) > 0 else None
        result = obj.reset_device(
            deviceResetList=deviceresetlist,
            projectId=projectid,
            workflowId=workflowid,
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


@pnp.command()
@click.option('--autosyncperiod', type=int,
              help='''SAVAMapping's autoSyncPeriod.''',
              default=None,
              show_default=True)
@click.option('--ccouser', type=str,
              help='''SAVAMapping's ccoUser.''',
              default=None,
              show_default=True)
@click.option('--expiry', type=int,
              help='''SAVAMapping's expiry.''',
              default=None,
              show_default=True)
@click.option('--lastsync', type=int,
              help='''SAVAMapping's lastSync.''',
              default=None,
              show_default=True)
@click.option('--profile', type=str,
              help='''SAVAMapping's profile.''',
              default=None,
              show_default=True)
@click.option('--smartaccountid', type=str,
              help='''SAVAMapping's smartAccountId.''',
              default=None,
              show_default=True)
@click.option('--syncresult', type=str,
              help='''SAVAMapping's syncResult.''',
              default=None,
              show_default=True)
@click.option('--syncresultstr', type=str,
              help='''SAVAMapping's syncResultStr.''',
              default=None,
              show_default=True)
@click.option('--syncstarttime', type=int,
              help='''SAVAMapping's syncStartTime.''',
              default=None,
              show_default=True)
@click.option('--syncstatus', type=str,
              help='''SAVAMapping's syncStatus. Available values are 'NOT_SYNCED', 'SYNCING', 'SUCCESS' and 'FAILURE'.''',
              default=None,
              show_default=True)
@click.option('--tenantid', type=str,
              help='''SAVAMapping's tenantId.''',
              default=None,
              show_default=True)
@click.option('--token', type=str,
              help='''SAVAMapping's token.''',
              default=None,
              show_default=True)
@click.option('--virtualaccountid', type=str,
              help='''SAVAMapping's virtualAccountId.''',
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
def sync_virtual_account_devices(obj, pretty_print, beep,
                                 autosyncperiod,
                                 ccouser,
                                 expiry,
                                 lastsync,
                                 profile,
                                 smartaccountid,
                                 syncresult,
                                 syncresultstr,
                                 syncstarttime,
                                 syncstatus,
                                 tenantid,
                                 token,
                                 virtualaccountid,
                                 headers,
                                 payload,
                                 active_validation):
    """Synchronizes the device info from the given smart account & virtual account with the PnP database. The response payload returns a list of synced devices.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        if profile is not None:
            profile = json.loads('{}'.format(profile))
        if syncresult is not None:
            syncresult = json.loads('{}'.format(syncresult))
        result = obj.sync_virtual_account_devices(
            autoSyncPeriod=autosyncperiod,
            ccoUser=ccouser,
            expiry=expiry,
            lastSync=lastsync,
            profile=profile,
            smartAccountId=smartaccountid,
            syncResult=syncresult,
            syncResultStr=syncresultstr,
            syncStartTime=syncstarttime,
            syncStatus=syncstatus,
            tenantId=tenantid,
            token=token,
            virtualAccountId=virtualaccountid,
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


@pnp.command()
@click.option('--limit', type=int,
              help='''Limits number of results.''',
              show_default=True)
@click.option('--offset', type=int,
              help='''Index of first result.''',
              show_default=True)
@click.option('--sort', type=str,
              help='''Comma seperated lost of fields to sort on.''',
              show_default=True)
@click.option('--sort_order', type=str,
              help='''Sort Order Ascending (asc) or Descending (des).''',
              show_default=True)
@click.option('--type', type=str,
              help='''Workflow Type.''',
              show_default=True)
@click.option('--name', type=str,
              help='''Workflow Name.''',
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
def get_workflows(obj, pretty_print, beep,
                  limit,
                  offset,
                  sort,
                  sort_order,
                  type,
                  name,
                  headers,
                  payload,
                  active_validation):
    """Returns the list of workflows based on filter criteria. If a limit is not specified, it will default to return 50 workflows. Pagination and sorting are also supported by this endpoint.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_workflows(
            limit=limit,
            offset=offset,
            sort=sort,
            sort_order=sort_order,
            type=type,
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


@pnp.command()
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
def delete_workflow_by_id(obj, pretty_print, beep,
                          id,
                          headers,
                          payload,
                          active_validation):
    """Deletes a workflow specified by id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.delete_workflow_by_id(
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


@pnp.command()
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
def get_device_by_id(obj, pretty_print, beep,
                     id,
                     headers,
                     payload,
                     active_validation):
    """Returns device details specified by device id.
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


@pnp.command()
@click.option('--domain', type=str,
              help='''Smart Account Domain.''',
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
def get_virtual_account_list(obj, pretty_print, beep,
                             domain,
                             headers,
                             payload,
                             active_validation):
    """Returns list of virtual accounts associated with the specified smart account.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_virtual_account_list(
            domain=domain,
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


@pnp.command()
@click.option('--deviceid', type=str,
              help='''SiteProvisionRequest's deviceId.''',
              default=None,
              show_default=True)
@click.option('--siteid', type=str,
              help='''SiteProvisionRequest's siteId.''',
              default=None,
              show_default=True)
@click.option('--type', type=str,
              help='''SiteProvisionRequest's type. Available values are 'Default', 'AccessPoint', 'StackSwitch', 'Sensor' and 'MobilityExpress'.''',
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
def preview_config(obj, pretty_print, beep,
                   deviceid,
                   siteid,
                   type,
                   headers,
                   payload,
                   active_validation):
    """Triggers a preview for site-based Day 0 Configuration.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.preview_config(
            deviceId=deviceid,
            siteId=siteid,
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


@pnp.command()
@click.option('--configfileurl', type=str,
              help='''ClaimDeviceRequest's configFileUrl.''',
              default=None,
              show_default=True)
@click.option('--configid', type=str,
              help='''ClaimDeviceRequest's configId.''',
              default=None,
              show_default=True)
@click.option('--deviceclaimlist', type=str, multiple=True,
              help='''ClaimDeviceRequest's deviceClaimList (list of objects).''',
              default=None,
              show_default=True)
@click.option('--fileserviceid', type=str,
              help='''ClaimDeviceRequest's fileServiceId.''',
              default=None,
              show_default=True)
@click.option('--imageid', type=str,
              help='''ClaimDeviceRequest's imageId.''',
              default=None,
              show_default=True)
@click.option('--imageurl', type=str,
              help='''ClaimDeviceRequest's imageUrl.''',
              default=None,
              show_default=True)
@click.option('--populateinventory', type=bool,
              help='''ClaimDeviceRequest's populateInventory.''',
              default=None,
              show_default=True)
@click.option('--projectid', type=str,
              help='''ClaimDeviceRequest's projectId.''',
              default=None,
              show_default=True)
@click.option('--workflowid', type=str,
              help='''ClaimDeviceRequest's workflowId.''',
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
def claim_device(obj, pretty_print, beep,
                 configfileurl,
                 configid,
                 deviceclaimlist,
                 fileserviceid,
                 imageid,
                 imageurl,
                 populateinventory,
                 projectid,
                 workflowid,
                 headers,
                 payload,
                 active_validation):
    """Claims one of more devices with specified workflow.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        deviceclaimlist = list(deviceclaimlist)
        deviceclaimlist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in deviceclaimlist)))
        deviceclaimlist = deviceclaimlist if len(deviceclaimlist) > 0 else None
        result = obj.claim_device(
            configFileUrl=configfileurl,
            configId=configid,
            deviceClaimList=deviceclaimlist,
            fileServiceId=fileserviceid,
            imageId=imageid,
            imageUrl=imageurl,
            populateInventory=populateinventory,
            projectId=projectid,
            workflowId=workflowid,
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


@pnp.command()
@click.option('--limit', type=int,
              help='''Limits number of results.''',
              show_default=True)
@click.option('--offset', type=int,
              help='''Index of first result.''',
              show_default=True)
@click.option('--sort', type=str,
              help='''Comma seperated list of fields to sort on.''',
              show_default=True)
@click.option('--sort_order', type=str,
              help='''Sort Order Ascending (asc) or Descending (des).''',
              show_default=True)
@click.option('--serial_number', type=str,
              help='''Device Serial Number.''',
              show_default=True)
@click.option('--state', type=str,
              help='''Device State.''',
              show_default=True)
@click.option('--onb_state', type=str,
              help='''Device Onboarding State.''',
              show_default=True)
@click.option('--cm_state', type=str,
              help='''Device Connection Manager State.''',
              show_default=True)
@click.option('--name', type=str,
              help='''Device Name.''',
              show_default=True)
@click.option('--pid', type=str,
              help='''Device ProductId.''',
              show_default=True)
@click.option('--source', type=str,
              help='''Device Source.''',
              show_default=True)
@click.option('--project_id', type=str,
              help='''Device Project Id.''',
              show_default=True)
@click.option('--workflow_id', type=str,
              help='''Device Workflow Id.''',
              show_default=True)
@click.option('--project_name', type=str,
              help='''Device Project Name.''',
              show_default=True)
@click.option('--workflow_name', type=str,
              help='''Device Workflow Name.''',
              show_default=True)
@click.option('--smart_account_id', type=str,
              help='''Device Smart Account.''',
              show_default=True)
@click.option('--virtual_account_id', type=str,
              help='''Device Virtual Account.''',
              show_default=True)
@click.option('--last_contact', type=bool,
              help='''Device Has Contacted lastContact > 0.''',
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
                    limit,
                    offset,
                    sort,
                    sort_order,
                    serial_number,
                    state,
                    onb_state,
                    cm_state,
                    name,
                    pid,
                    source,
                    project_id,
                    workflow_id,
                    project_name,
                    workflow_name,
                    smart_account_id,
                    virtual_account_id,
                    last_contact,
                    headers,
                    payload,
                    active_validation):
    """Returns list of devices based on filter crieteria. If a limit is not specified, it will default to return 50 devices. Pagination and sorting are also supported by this endpoint.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_list(
            limit=limit,
            offset=offset,
            sort=sort,
            sort_order=sort_order,
            serial_number=serial_number,
            state=state,
            onb_state=onb_state,
            cm_state=cm_state,
            name=name,
            pid=pid,
            source=source,
            project_id=project_id,
            workflow_id=workflow_id,
            project_name=project_name,
            workflow_name=workflow_name,
            smart_account_id=smart_account_id,
            virtual_account_id=virtual_account_id,
            last_contact=last_contact,
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


@pnp.command()
@click.option('--_id', type=str,
              help='''Workflow's _id.''',
              default=None,
              show_default=True)
@click.option('--addtoinventory', type=bool,
              help='''Workflow's addToInventory.''',
              default=None,
              show_default=True)
@click.option('--addedon', type=int,
              help='''Workflow's addedOn.''',
              default=None,
              show_default=True)
@click.option('--configid', type=str,
              help='''Workflow's configId.''',
              default=None,
              show_default=True)
@click.option('--currtaskidx', type=int,
              help='''Workflow's currTaskIdx.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''Workflow's description.''',
              default=None,
              show_default=True)
@click.option('--endtime', type=int,
              help='''Workflow's endTime.''',
              default=None,
              show_default=True)
@click.option('--exectime', type=int,
              help='''Workflow's execTime.''',
              default=None,
              show_default=True)
@click.option('--imageid', type=str,
              help='''Workflow's imageId.''',
              default=None,
              show_default=True)
@click.option('--instancetype', type=str,
              help='''Workflow's instanceType. Available values are 'SystemWorkflow', 'UserWorkflow' and 'SystemResetWorkflow'.''',
              default=None,
              show_default=True)
@click.option('--lastupdateon', type=int,
              help='''Workflow's lastupdateOn.''',
              default=None,
              show_default=True)
@click.option('--name', type=str,
              help='''Workflow's name.''',
              default=None,
              show_default=True)
@click.option('--starttime', type=int,
              help='''Workflow's startTime.''',
              default=None,
              show_default=True)
@click.option('--state', type=str,
              help='''Workflow's state.''',
              default=None,
              show_default=True)
@click.option('--tasks', type=str, multiple=True,
              help='''Workflow's tasks (list of objects).''',
              default=None,
              show_default=True)
@click.option('--tenantid', type=str,
              help='''Workflow's tenantId.''',
              default=None,
              show_default=True)
@click.option('--type', type=str,
              help='''Workflow's type.''',
              default=None,
              show_default=True)
@click.option('--usestate', type=str,
              help='''Workflow's useState.''',
              default=None,
              show_default=True)
@click.option('--version', type=int,
              help='''Workflow's version.''',
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
def add_a_workflow(obj, pretty_print, beep,
                   _id,
                   addtoinventory,
                   addedon,
                   configid,
                   currtaskidx,
                   description,
                   endtime,
                   exectime,
                   imageid,
                   instancetype,
                   lastupdateon,
                   name,
                   starttime,
                   state,
                   tasks,
                   tenantid,
                   type,
                   usestate,
                   version,
                   headers,
                   payload,
                   active_validation):
    """Adds a PnP Workflow along with the relevant tasks in the workflow into the PnP database.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        tasks = list(tasks)
        tasks = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in tasks)))
        tasks = tasks if len(tasks) > 0 else None
        result = obj.add_a_workflow(
            _id=_id,
            addToInventory=addtoinventory,
            addedOn=addedon,
            configId=configid,
            currTaskIdx=currtaskidx,
            description=description,
            endTime=endtime,
            execTime=exectime,
            imageId=imageid,
            instanceType=instancetype,
            lastupdateOn=lastupdateon,
            name=name,
            startTime=starttime,
            state=state,
            tasks=tasks,
            tenantId=tenantid,
            type=type,
            useState=usestate,
            version=version,
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


@pnp.command()
@click.option('--serial_number', type=str,
              help='''Device Serial Number.''',
              show_default=True)
@click.option('--state', type=str,
              help='''Device State.''',
              show_default=True)
@click.option('--onb_state', type=str,
              help='''Device Onboarding State.''',
              show_default=True)
@click.option('--cm_state', type=str,
              help='''Device Connection Manager State.''',
              show_default=True)
@click.option('--name', type=str,
              help='''Device Name.''',
              show_default=True)
@click.option('--pid', type=str,
              help='''Device ProductId.''',
              show_default=True)
@click.option('--source', type=str,
              help='''Device Source.''',
              show_default=True)
@click.option('--project_id', type=str,
              help='''Device Project Id.''',
              show_default=True)
@click.option('--workflow_id', type=str,
              help='''Device Workflow Id.''',
              show_default=True)
@click.option('--project_name', type=str,
              help='''Device Project Name.''',
              show_default=True)
@click.option('--workflow_name', type=str,
              help='''Device Workflow Name.''',
              show_default=True)
@click.option('--smart_account_id', type=str,
              help='''Device Smart Account.''',
              show_default=True)
@click.option('--virtual_account_id', type=str,
              help='''Device Virtual Account.''',
              show_default=True)
@click.option('--last_contact', type=bool,
              help='''Device Has Contacted lastContact > 0.''',
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
def get_device_count(obj, pretty_print, beep,
                     serial_number,
                     state,
                     onb_state,
                     cm_state,
                     name,
                     pid,
                     source,
                     project_id,
                     workflow_id,
                     project_name,
                     workflow_name,
                     smart_account_id,
                     virtual_account_id,
                     last_contact,
                     headers,
                     payload,
                     active_validation):
    """Returns the device count based on filter criteria. This is useful for pagination.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_count(
            serial_number=serial_number,
            state=state,
            onb_state=onb_state,
            cm_state=cm_state,
            name=name,
            pid=pid,
            source=source,
            project_id=project_id,
            workflow_id=workflow_id,
            project_name=project_name,
            workflow_name=workflow_name,
            smart_account_id=smart_account_id,
            virtual_account_id=virtual_account_id,
            last_contact=last_contact,
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


@pnp.command()
@click.option('--serial_number', type=str,
              help='''Device Serial Number.''',
              required=True,
              show_default=True)
@click.option('--sort', type=str,
              help='''Comma seperated list of fields to sort on.''',
              show_default=True)
@click.option('--sort_order', type=str,
              help='''Sort Order Ascending (asc) or Descending (des).''',
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
def get_device_history(obj, pretty_print, beep,
                       serial_number,
                       sort,
                       sort_order,
                       headers,
                       payload,
                       active_validation):
    """Returns history for a specific device. Serial number is a required parameter.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_device_history(
            serial_number=serial_number,
            sort=sort,
            sort_order=sort_order,
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


@pnp.command()
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
def delete_device_by_id_from_pnp(obj, pretty_print, beep,
                                 id,
                                 headers,
                                 payload,
                                 active_validation):
    """Deletes specified device from PnP database.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.delete_device_by_id_from_pnp(
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


@pnp.command()
@click.option('--_id', type=str,
              help='''Device's _id.''',
              default=None,
              show_default=True)
@click.option('--deviceinfo', type=str,
              help='''Device's deviceInfo.''',
              default=None,
              show_default=True)
@click.option('--runsummarylist', type=str, multiple=True,
              help='''Device's runSummaryList (list of objects).''',
              default=None,
              show_default=True)
@click.option('--systemresetworkflow', type=str,
              help='''Device's systemResetWorkflow.''',
              default=None,
              show_default=True)
@click.option('--systemworkflow', type=str,
              help='''Device's systemWorkflow.''',
              default=None,
              show_default=True)
@click.option('--tenantid', type=str,
              help='''Device's tenantId.''',
              default=None,
              show_default=True)
@click.option('--version', type=int,
              help='''Device's version.''',
              default=None,
              show_default=True)
@click.option('--workflow', type=str,
              help='''Device's workflow.''',
              default=None,
              show_default=True)
@click.option('--workflowparameters', type=str,
              help='''Device's workflowParameters.''',
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
               _id,
               deviceinfo,
               runsummarylist,
               systemresetworkflow,
               systemworkflow,
               tenantid,
               version,
               workflow,
               workflowparameters,
               headers,
               payload,
               active_validation):
    """Adds a device to the PnP database.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        if deviceinfo is not None:
            deviceinfo = json.loads('{}'.format(deviceinfo))
        runsummarylist = list(runsummarylist)
        runsummarylist = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in runsummarylist)))
        runsummarylist = runsummarylist if len(runsummarylist) > 0 else None
        if systemresetworkflow is not None:
            systemresetworkflow = json.loads('{}'.format(systemresetworkflow))
        if systemworkflow is not None:
            systemworkflow = json.loads('{}'.format(systemworkflow))
        if workflow is not None:
            workflow = json.loads('{}'.format(workflow))
        if workflowparameters is not None:
            workflowparameters = json.loads('{}'.format(workflowparameters))
        result = obj.add_device(
            _id=_id,
            deviceInfo=deviceinfo,
            runSummaryList=runsummarylist,
            systemResetWorkflow=systemresetworkflow,
            systemWorkflow=systemworkflow,
            tenantId=tenantid,
            version=version,
            workflow=workflow,
            workflowParameters=workflowparameters,
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
