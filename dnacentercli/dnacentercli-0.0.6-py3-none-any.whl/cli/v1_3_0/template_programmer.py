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
def template_programmer(ctx, obj):
    """DNA Center Template Programmer API (version: 1.3.0).

    Wraps the DNA Center Template Programmer API and exposes the API as native Python commands.

    """
    ctx.obj = obj.template_programmer


@template_programmer.command()
@click.option('--createtime', type=int,
              help='''ProjectDTO's createTime.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''ProjectDTO's description.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''ProjectDTO's id.''',
              default=None,
              show_default=True)
@click.option('--lastupdatetime', type=int,
              help='''ProjectDTO's lastUpdateTime.''',
              default=None,
              show_default=True)
@click.option('--name', type=str,
              help='''ProjectDTO's name.''',
              default=None,
              show_default=True)
@click.option('--tags', type=str, multiple=True,
              help='''ProjectDTO's tags (list of string, objects).''',
              default=None,
              show_default=True)
@click.option('--templates',
              help='''Part of the JSON serializable Python object to send in the body of the Request.''',
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
def create_project(obj, pretty_print, beep,
                   createtime,
                   description,
                   id,
                   lastupdatetime,
                   name,
                   tags,
                   templates,
                   headers,
                   payload,
                   active_validation):
    """Creates a new project.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        tags = list(tags)
        tags = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in tags)))
        tags = tags if len(tags) > 0 else None
        result = obj.create_project(
            createTime=createtime,
            description=description,
            id=id,
            lastUpdateTime=lastupdatetime,
            name=name,
            tags=tags,
            templates=templates,
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


@template_programmer.command()
@click.option('--project_id', type=str,
              help='''projectId query parameter.''',
              show_default=True)
@click.option('--software_type', type=str,
              help='''softwareType query parameter.''',
              show_default=True)
@click.option('--software_version', type=str,
              help='''softwareVersion query parameter.''',
              show_default=True)
@click.option('--product_family', type=str,
              help='''productFamily query parameter.''',
              show_default=True)
@click.option('--product_series', type=str,
              help='''productSeries query parameter.''',
              show_default=True)
@click.option('--product_type', type=str,
              help='''productType query parameter.''',
              show_default=True)
@click.option('--filter_conflicting_templates', type=bool,
              help='''filterConflictingTemplates query parameter.''',
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
def gets_the_templates_available(obj, pretty_print, beep,
                                 project_id,
                                 software_type,
                                 software_version,
                                 product_family,
                                 product_series,
                                 product_type,
                                 filter_conflicting_templates,
                                 headers,
                                 payload,
                                 active_validation):
    """List the templates available.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.gets_the_templates_available(
            project_id=project_id,
            software_type=software_type,
            software_version=software_version,
            product_family=product_family,
            product_series=product_series,
            product_type=product_type,
            filter_conflicting_templates=filter_conflicting_templates,
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


@template_programmer.command()
@click.option('--name', type=str,
              help='''Name of project to be searched.''',
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
def get_projects(obj, pretty_print, beep,
                 name,
                 headers,
                 payload,
                 active_validation):
    """Returns the projects in the system.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_projects(
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


@template_programmer.command()
@click.option('--forcepushtemplate', type=bool,
              help='''TemplateDeploymentInfo's forcePushTemplate.''',
              default=None,
              show_default=True)
@click.option('--iscomposite', type=bool,
              help='''TemplateDeploymentInfo's isComposite.''',
              default=None,
              show_default=True)
@click.option('--maintemplateid', type=str,
              help='''TemplateDeploymentInfo's mainTemplateId.''',
              default=None,
              show_default=True)
@click.option('--membertemplatedeploymentinfo', type=str, multiple=True,
              help='''TemplateDeploymentInfo's memberTemplateDeploymentInfo (list of any objects).''',
              default=None,
              show_default=True)
@click.option('--targetinfo', type=str, multiple=True,
              help='''TemplateDeploymentInfo's targetInfo (list of objects).''',
              default=None,
              show_default=True)
@click.option('--templateid', type=str,
              help='''TemplateDeploymentInfo's templateId.''',
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
def deploy_template(obj, pretty_print, beep,
                    forcepushtemplate,
                    iscomposite,
                    maintemplateid,
                    membertemplatedeploymentinfo,
                    targetinfo,
                    templateid,
                    headers,
                    payload,
                    active_validation):
    """Deploys a template.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        membertemplatedeploymentinfo = list(membertemplatedeploymentinfo)
        membertemplatedeploymentinfo = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in membertemplatedeploymentinfo)))
        membertemplatedeploymentinfo = membertemplatedeploymentinfo if len(membertemplatedeploymentinfo) > 0 else None
        targetinfo = list(targetinfo)
        targetinfo = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in targetinfo)))
        targetinfo = targetinfo if len(targetinfo) > 0 else None
        result = obj.deploy_template(
            forcePushTemplate=forcepushtemplate,
            isComposite=iscomposite,
            mainTemplateId=maintemplateid,
            memberTemplateDeploymentInfo=membertemplatedeploymentinfo,
            targetInfo=targetinfo,
            templateId=templateid,
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


@template_programmer.command()
@click.option('--author', type=str,
              help='''TemplateDTO's author.''',
              default=None,
              show_default=True)
@click.option('--composite', type=bool,
              help='''TemplateDTO's composite.''',
              default=None,
              show_default=True)
@click.option('--containingtemplates', type=str, multiple=True,
              help='''TemplateDTO's containingTemplates (list of objects).''',
              default=None,
              show_default=True)
@click.option('--createtime', type=int,
              help='''TemplateDTO's createTime.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''TemplateDTO's description.''',
              default=None,
              show_default=True)
@click.option('--devicetypes', type=str, multiple=True,
              help='''TemplateDTO's deviceTypes (list of objects).''',
              default=None,
              show_default=True)
@click.option('--failurepolicy', type=str,
              help='''TemplateDTO's failurePolicy. Available values are 'ABORT_ON_ERROR', 'CONTINUE_ON_ERROR', 'ROLLBACK_ON_ERROR', 'ROLLBACK_TARGET_ON_ERROR' and 'ABORT_TARGET_ON_ERROR'.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''TemplateDTO's id.''',
              default=None,
              show_default=True)
@click.option('--lastupdatetime', type=int,
              help='''TemplateDTO's lastUpdateTime.''',
              default=None,
              show_default=True)
@click.option('--name', type=str,
              help='''TemplateDTO's name.''',
              default=None,
              show_default=True)
@click.option('--parenttemplateid', type=str,
              help='''TemplateDTO's parentTemplateId.''',
              default=None,
              show_default=True)
@click.option('--projectid', type=str,
              help='''TemplateDTO's projectId.''',
              default=None,
              show_default=True)
@click.option('--projectname', type=str,
              help='''TemplateDTO's projectName.''',
              default=None,
              show_default=True)
@click.option('--rollbacktemplatecontent', type=str,
              help='''TemplateDTO's rollbackTemplateContent.''',
              default=None,
              show_default=True)
@click.option('--rollbacktemplateparams', type=str, multiple=True,
              help='''TemplateDTO's rollbackTemplateParams (list of objects).''',
              default=None,
              show_default=True)
@click.option('--softwaretype', type=str,
              help='''TemplateDTO's softwareType.''',
              default=None,
              show_default=True)
@click.option('--softwarevariant', type=str,
              help='''TemplateDTO's softwareVariant.''',
              default=None,
              show_default=True)
@click.option('--softwareversion', type=str,
              help='''TemplateDTO's softwareVersion.''',
              default=None,
              show_default=True)
@click.option('--tags', type=str, multiple=True,
              help='''TemplateDTO's tags (list of string, objects).''',
              default=None,
              show_default=True)
@click.option('--templatecontent', type=str,
              help='''TemplateDTO's templateContent.''',
              default=None,
              show_default=True)
@click.option('--templateparams', type=str, multiple=True,
              help='''TemplateDTO's templateParams (list of objects).''',
              default=None,
              show_default=True)
@click.option('--version', type=str,
              help='''TemplateDTO's version.''',
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
def update_template(obj, pretty_print, beep,
                    author,
                    composite,
                    containingtemplates,
                    createtime,
                    description,
                    devicetypes,
                    failurepolicy,
                    id,
                    lastupdatetime,
                    name,
                    parenttemplateid,
                    projectid,
                    projectname,
                    rollbacktemplatecontent,
                    rollbacktemplateparams,
                    softwaretype,
                    softwarevariant,
                    softwareversion,
                    tags,
                    templatecontent,
                    templateparams,
                    version,
                    headers,
                    payload,
                    active_validation):
    """Updates an existing template.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        containingtemplates = list(containingtemplates)
        containingtemplates = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in containingtemplates)))
        containingtemplates = containingtemplates if len(containingtemplates) > 0 else None
        devicetypes = list(devicetypes)
        devicetypes = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in devicetypes)))
        devicetypes = devicetypes if len(devicetypes) > 0 else None
        rollbacktemplateparams = list(rollbacktemplateparams)
        rollbacktemplateparams = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in rollbacktemplateparams)))
        rollbacktemplateparams = rollbacktemplateparams if len(rollbacktemplateparams) > 0 else None
        tags = list(tags)
        tags = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in tags)))
        tags = tags if len(tags) > 0 else None
        templateparams = list(templateparams)
        templateparams = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in templateparams)))
        templateparams = templateparams if len(templateparams) > 0 else None
        result = obj.update_template(
            author=author,
            composite=composite,
            containingTemplates=containingtemplates,
            createTime=createtime,
            description=description,
            deviceTypes=devicetypes,
            failurePolicy=failurepolicy,
            id=id,
            lastUpdateTime=lastupdatetime,
            name=name,
            parentTemplateId=parenttemplateid,
            projectId=projectid,
            projectName=projectname,
            rollbackTemplateContent=rollbacktemplatecontent,
            rollbackTemplateParams=rollbacktemplateparams,
            softwareType=softwaretype,
            softwareVariant=softwarevariant,
            softwareVersion=softwareversion,
            tags=tags,
            templateContent=templatecontent,
            templateParams=templateparams,
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


@template_programmer.command()
@click.option('--createtime', type=int,
              help='''ProjectDTO's createTime.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''ProjectDTO's description.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''ProjectDTO's id.''',
              default=None,
              show_default=True)
@click.option('--lastupdatetime', type=int,
              help='''ProjectDTO's lastUpdateTime.''',
              default=None,
              show_default=True)
@click.option('--name', type=str,
              help='''ProjectDTO's name.''',
              default=None,
              show_default=True)
@click.option('--tags', type=str, multiple=True,
              help='''ProjectDTO's tags (list of string, objects).''',
              default=None,
              show_default=True)
@click.option('--templates',
              help='''Part of the JSON serializable Python object to send in the body of the Request.''',
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
def update_project(obj, pretty_print, beep,
                   createtime,
                   description,
                   id,
                   lastupdatetime,
                   name,
                   tags,
                   templates,
                   headers,
                   payload,
                   active_validation):
    """Updates an existing project.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        tags = list(tags)
        tags = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in tags)))
        tags = tags if len(tags) > 0 else None
        result = obj.update_project(
            createTime=createtime,
            description=description,
            id=id,
            lastUpdateTime=lastupdatetime,
            name=name,
            tags=tags,
            templates=templates,
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


@template_programmer.command()
@click.option('--template_id', type=str,
              help='''templateId path parameter.''',
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
def delete_template(obj, pretty_print, beep,
                    template_id,
                    headers,
                    payload,
                    active_validation):
    """Deletes an existing template.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.delete_template(
            template_id=template_id,
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


@template_programmer.command()
@click.option('--params', type=str,
              help='''TemplatePreviewRequestDTO's params.''',
              default=None,
              show_default=True)
@click.option('--templateid', type=str,
              help='''TemplatePreviewRequestDTO's templateId.''',
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
def preview_template(obj, pretty_print, beep,
                     params,
                     templateid,
                     headers,
                     payload,
                     active_validation):
    """Previews an existing template.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        if params is not None:
            params = json.loads('{}'.format(params))
        result = obj.preview_template(
            params=params,
            templateId=templateid,
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


@template_programmer.command()
@click.option('--template_id', type=str,
              help='''templateId path parameter.''',
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
def get_template_versions(obj, pretty_print, beep,
                          template_id,
                          headers,
                          payload,
                          active_validation):
    """Returns the versions of a specified template.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_template_versions(
            template_id=template_id,
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


@template_programmer.command()
@click.option('--comments', type=str,
              help='''TemplateVersionRequestDTO's comments.''',
              default=None,
              show_default=True)
@click.option('--templateid', type=str,
              help='''TemplateVersionRequestDTO's templateId.''',
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
def version_template(obj, pretty_print, beep,
                     comments,
                     templateid,
                     headers,
                     payload,
                     active_validation):
    """Creates Versioning for the current contents of the template.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.version_template(
            comments=comments,
            templateId=templateid,
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


@template_programmer.command()
@click.option('--latest_version', type=bool,
              help='''latestVersion query parameter.''',
              show_default=True)
@click.option('--template_id', type=str,
              help='''templateId path parameter.''',
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
def get_template_details(obj, pretty_print, beep,
                         latest_version,
                         template_id,
                         headers,
                         payload,
                         active_validation):
    """Returns details of the specified template.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_template_details(
            latest_version=latest_version,
            template_id=template_id,
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


@template_programmer.command()
@click.option('--author', type=str,
              help='''TemplateDTO's author.''',
              default=None,
              show_default=True)
@click.option('--composite', type=bool,
              help='''TemplateDTO's composite.''',
              default=None,
              show_default=True)
@click.option('--containingtemplates', type=str, multiple=True,
              help='''TemplateDTO's containingTemplates (list of objects).''',
              default=None,
              show_default=True)
@click.option('--createtime', type=int,
              help='''TemplateDTO's createTime.''',
              default=None,
              show_default=True)
@click.option('--description', type=str,
              help='''TemplateDTO's description.''',
              default=None,
              show_default=True)
@click.option('--devicetypes', type=str, multiple=True,
              help='''TemplateDTO's deviceTypes (list of objects).''',
              default=None,
              show_default=True)
@click.option('--failurepolicy', type=str,
              help='''TemplateDTO's failurePolicy. Available values are 'ABORT_ON_ERROR', 'CONTINUE_ON_ERROR', 'ROLLBACK_ON_ERROR', 'ROLLBACK_TARGET_ON_ERROR' and 'ABORT_TARGET_ON_ERROR'.''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''TemplateDTO's id.''',
              default=None,
              show_default=True)
@click.option('--lastupdatetime', type=int,
              help='''TemplateDTO's lastUpdateTime.''',
              default=None,
              show_default=True)
@click.option('--name', type=str,
              help='''TemplateDTO's name.''',
              default=None,
              show_default=True)
@click.option('--parenttemplateid', type=str,
              help='''TemplateDTO's parentTemplateId.''',
              default=None,
              show_default=True)
@click.option('--projectid', type=str,
              help='''TemplateDTO's projectId.''',
              default=None,
              show_default=True)
@click.option('--projectname', type=str,
              help='''TemplateDTO's projectName.''',
              default=None,
              show_default=True)
@click.option('--rollbacktemplatecontent', type=str,
              help='''TemplateDTO's rollbackTemplateContent.''',
              default=None,
              show_default=True)
@click.option('--rollbacktemplateparams', type=str, multiple=True,
              help='''TemplateDTO's rollbackTemplateParams (list of objects).''',
              default=None,
              show_default=True)
@click.option('--softwaretype', type=str,
              help='''TemplateDTO's softwareType.''',
              default=None,
              show_default=True)
@click.option('--softwarevariant', type=str,
              help='''TemplateDTO's softwareVariant.''',
              default=None,
              show_default=True)
@click.option('--softwareversion', type=str,
              help='''TemplateDTO's softwareVersion.''',
              default=None,
              show_default=True)
@click.option('--tags', type=str, multiple=True,
              help='''TemplateDTO's tags (list of string, objects).''',
              default=None,
              show_default=True)
@click.option('--templatecontent', type=str,
              help='''TemplateDTO's templateContent.''',
              default=None,
              show_default=True)
@click.option('--templateparams', type=str, multiple=True,
              help='''TemplateDTO's templateParams (list of objects).''',
              default=None,
              show_default=True)
@click.option('--version', type=str,
              help='''TemplateDTO's version.''',
              default=None,
              show_default=True)
@click.option('--project_id', type=str,
              help='''projectId path parameter.''',
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
def create_template(obj, pretty_print, beep,
                    author,
                    composite,
                    containingtemplates,
                    createtime,
                    description,
                    devicetypes,
                    failurepolicy,
                    id,
                    lastupdatetime,
                    name,
                    parenttemplateid,
                    projectid,
                    projectname,
                    rollbacktemplatecontent,
                    rollbacktemplateparams,
                    softwaretype,
                    softwarevariant,
                    softwareversion,
                    tags,
                    templatecontent,
                    templateparams,
                    version,
                    project_id,
                    headers,
                    payload,
                    active_validation):
    """Creates a new template.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        containingtemplates = list(containingtemplates)
        containingtemplates = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in containingtemplates)))
        containingtemplates = containingtemplates if len(containingtemplates) > 0 else None
        devicetypes = list(devicetypes)
        devicetypes = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in devicetypes)))
        devicetypes = devicetypes if len(devicetypes) > 0 else None
        rollbacktemplateparams = list(rollbacktemplateparams)
        rollbacktemplateparams = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in rollbacktemplateparams)))
        rollbacktemplateparams = rollbacktemplateparams if len(rollbacktemplateparams) > 0 else None
        tags = list(tags)
        tags = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in tags)))
        tags = tags if len(tags) > 0 else None
        templateparams = list(templateparams)
        templateparams = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in templateparams)))
        templateparams = templateparams if len(templateparams) > 0 else None
        result = obj.create_template(
            author=author,
            composite=composite,
            containingTemplates=containingtemplates,
            createTime=createtime,
            description=description,
            deviceTypes=devicetypes,
            failurePolicy=failurepolicy,
            id=id,
            lastUpdateTime=lastupdatetime,
            name=name,
            parentTemplateId=parenttemplateid,
            projectId=projectid,
            projectName=projectname,
            rollbackTemplateContent=rollbacktemplatecontent,
            rollbackTemplateParams=rollbacktemplateparams,
            softwareType=softwaretype,
            softwareVariant=softwarevariant,
            softwareVersion=softwareversion,
            tags=tags,
            templateContent=templatecontent,
            templateParams=templateparams,
            version=version,
            project_id=project_id,
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


@template_programmer.command()
@click.option('--deployment_id', type=str,
              help='''deploymentId path parameter.''',
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
def get_template_deployment_status(obj, pretty_print, beep,
                                   deployment_id,
                                   headers,
                                   payload,
                                   active_validation):
    """Returns the status of a deployed template.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_template_deployment_status(
            deployment_id=deployment_id,
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


@template_programmer.command()
@click.option('--project_id', type=str,
              help='''projectId path parameter.''',
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
def delete_project(obj, pretty_print, beep,
                   project_id,
                   headers,
                   payload,
                   active_validation):
    """Deletes an existing Project.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.delete_project(
            project_id=project_id,
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
