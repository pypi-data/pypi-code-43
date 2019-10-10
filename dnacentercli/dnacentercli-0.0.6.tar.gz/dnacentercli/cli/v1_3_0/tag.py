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
def tag(ctx, obj):
    """DNA Center Tag API (version: 1.3.0).

    Wraps the DNA Center Tag API and exposes the API as native Python commands.

    """
    ctx.obj = obj.tag


@tag.command()
@click.option('--id', type=str,
              help='''Tag ID.''',
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
def add_members_to_the_tag(obj, pretty_print, beep,
                           id,
                           headers,
                           payload,
                           active_validation):
    """Adds members to the tag specified by id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.add_members_to_the_tag(
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


@tag.command()
@click.option('--description', type=str,
              help='''TagDTO's description.''',
              default=None,
              show_default=True)
@click.option('--dynamicrules', type=str, multiple=True,
              help='''TagDTO's dynamicRules (list of objects).''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''TagDTO's id.''',
              default=None,
              show_default=True)
@click.option('--instancetenantid', type=str,
              help='''TagDTO's instanceTenantId.''',
              default=None,
              show_default=True)
@click.option('--name', type=str,
              help='''TagDTO's name.''',
              default=None,
              show_default=True)
@click.option('--systemtag', type=bool,
              help='''TagDTO's systemTag.''',
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
def create_tag(obj, pretty_print, beep,
               description,
               dynamicrules,
               id,
               instancetenantid,
               name,
               systemtag,
               headers,
               payload,
               active_validation):
    """Creates tag with specified tag attributes.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        dynamicrules = list(dynamicrules)
        dynamicrules = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in dynamicrules)))
        dynamicrules = dynamicrules if len(dynamicrules) > 0 else None
        result = obj.create_tag(
            description=description,
            dynamicRules=dynamicrules,
            id=id,
            instanceTenantId=instancetenantid,
            name=name,
            systemTag=systemtag,
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


@tag.command()
@click.option('--id', type=str,
              help='''Tag ID.''',
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
def delete_tag(obj, pretty_print, beep,
               id,
               headers,
               payload,
               active_validation):
    """Deletes a tag specified by id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.delete_tag(
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


@tag.command()
@click.option('--member_type', type=str,
              help='''memberType query parameter.''',
              required=True,
              show_default=True)
@click.option('--member_association_type', type=str,
              help='''memberAssociationType query parameter.''',
              show_default=True)
@click.option('--level', type=str,
              help='''level query parameter.''',
              show_default=True)
@click.option('--id', type=str,
              help='''Tag ID.''',
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
def get_tag_member_count(obj, pretty_print, beep,
                         member_type,
                         member_association_type,
                         level,
                         id,
                         headers,
                         payload,
                         active_validation):
    """Returns the number of members in a given tag.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_tag_member_count(
            member_type=member_type,
            member_association_type=member_association_type,
            level=level,
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


@tag.command()
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
def get_tag_resource_types(obj, pretty_print, beep,
                           headers,
                           payload,
                           active_validation):
    """Returns list of supported resource types.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_tag_resource_types(
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


@tag.command()
@click.option('--membertotags', type=str,
              help='''TagMemberDTO's memberToTags.''',
              default=None,
              show_default=True)
@click.option('--membertype', type=str,
              help='''TagMemberDTO's memberType.''',
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
def updates_tag_membership(obj, pretty_print, beep,
                           membertotags,
                           membertype,
                           headers,
                           payload,
                           active_validation):
    """Updates tag membership. As part of the request payload through this API, only the specified members are added / retained to the given input tags. Possible values of memberType attribute in the request payload can be queried by using the /tag/member/type API.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        if membertotags is not None:
            membertotags = json.loads('{}'.format(membertotags))
        result = obj.updates_tag_membership(
            memberToTags=membertotags,
            memberType=membertype,
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


@tag.command()
@click.option('--description', type=str,
              help='''TagDTO's description.''',
              default=None,
              show_default=True)
@click.option('--dynamicrules', type=str, multiple=True,
              help='''TagDTO's dynamicRules (list of objects).''',
              default=None,
              show_default=True)
@click.option('--id', type=str,
              help='''TagDTO's id.''',
              default=None,
              show_default=True)
@click.option('--instancetenantid', type=str,
              help='''TagDTO's instanceTenantId.''',
              default=None,
              show_default=True)
@click.option('--name', type=str,
              help='''TagDTO's name.''',
              default=None,
              show_default=True)
@click.option('--systemtag', type=bool,
              help='''TagDTO's systemTag.''',
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
def update_tag(obj, pretty_print, beep,
               description,
               dynamicrules,
               id,
               instancetenantid,
               name,
               systemtag,
               headers,
               payload,
               active_validation):
    """Updates a tag specified by id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        dynamicrules = list(dynamicrules)
        dynamicrules = json.loads('[{}]'.format(', '.join('{0}'.format(w) for w in dynamicrules)))
        dynamicrules = dynamicrules if len(dynamicrules) > 0 else None
        result = obj.update_tag(
            description=description,
            dynamicRules=dynamicrules,
            id=id,
            instanceTenantId=instancetenantid,
            name=name,
            systemTag=systemtag,
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


@tag.command()
@click.option('--name', type=str,
              help='''name query parameter.''',
              show_default=True)
@click.option('--name_space', type=str,
              help='''nameSpace query parameter.''',
              show_default=True)
@click.option('--attribute_name', type=str,
              help='''attributeName query parameter.''',
              show_default=True)
@click.option('--level', type=str,
              help='''level query parameter.''',
              show_default=True)
@click.option('--size', type=str,
              help='''size in kilobytes(KB).''',
              show_default=True)
@click.option('--system_tag', type=str,
              help='''systemTag query parameter.''',
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
def get_tag_count(obj, pretty_print, beep,
                  name,
                  name_space,
                  attribute_name,
                  level,
                  size,
                  system_tag,
                  headers,
                  payload,
                  active_validation):
    """Returns tag count.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_tag_count(
            name=name,
            name_space=name_space,
            attribute_name=attribute_name,
            level=level,
            size=size,
            system_tag=system_tag,
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


@tag.command()
@click.option('--id', type=str,
              help='''Tag ID.''',
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
def get_tag_by_id(obj, pretty_print, beep,
                  id,
                  headers,
                  payload,
                  active_validation):
    """Returns tag specified by Id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_tag_by_id(
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


@tag.command()
@click.option('--member_type', type=str,
              help='''Entity type of the member. Possible values can be retrieved by using /tag/member/type API.''',
              required=True,
              show_default=True)
@click.option('--offset', type=str,
              help='''Used for pagination. It indicates the starting row number out of available member records.''',
              show_default=True)
@click.option('--limit', type=str,
              help='''Used to Number of maximum members to return in the result.''',
              show_default=True)
@click.option('--member_association_type', type=str,
              help='''Indicates how the member is associated with the tag. Possible values and description. 1) DYNAMIC The member is associated to the tag through rules. 2) STATIC – The member is associated to the tag manually. 3) MIXED – The member is associated manually and also satisfies the rule defined for the tag.''',
              show_default=True)
@click.option('--level', type=str,
              help='''level query parameter.''',
              show_default=True)
@click.option('--id', type=str,
              help='''Tag ID.''',
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
def get_tag_members_by_id(obj, pretty_print, beep,
                          member_type,
                          offset,
                          limit,
                          member_association_type,
                          level,
                          id,
                          headers,
                          payload,
                          active_validation):
    """Returns tag members specified by id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_tag_members_by_id(
            member_type=member_type,
            offset=offset,
            limit=limit,
            member_association_type=member_association_type,
            level=level,
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


@tag.command()
@click.option('--id', type=str,
              help='''Tag ID.''',
              required=True,
              show_default=True)
@click.option('--member_id', type=str,
              help='''TagMember id to be removed from tag.''',
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
def remove_tag_member(obj, pretty_print, beep,
                      id,
                      member_id,
                      headers,
                      payload,
                      active_validation):
    """Removes Tag member from the tag specified by id.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.remove_tag_member(
            id=id,
            member_id=member_id,
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


@tag.command()
@click.option('--name', type=str,
              help='''Tag name is mandatory when filter operation is used.''',
              show_default=True)
@click.option('--additional_info_name_space', type=str,
              help='''additionalInfo.nameSpace query parameter.''',
              show_default=True)
@click.option('--additional_info_attributes', type=str,
              help='''additionalInfo.attributes query parameter.''',
              show_default=True)
@click.option('--level', type=str,
              help='''level query parameter.''',
              show_default=True)
@click.option('--offset', type=str,
              help='''offset query parameter.''',
              show_default=True)
@click.option('--limit', type=str,
              help='''limit query parameter.''',
              show_default=True)
@click.option('--size', type=str,
              help='''size in kilobytes(KB).''',
              show_default=True)
@click.option('--field', type=str,
              help='''Available field names are :'name,id,parentId,type,additionalInfo.nameSpace,additionalInfo.attributes'.''',
              show_default=True)
@click.option('--sort_by', type=str,
              help='''Only supported attribute is name. SortyBy is mandatory when order is used.''',
              show_default=True)
@click.option('--order', type=str,
              help='''Available values are asc and des.''',
              show_default=True)
@click.option('--system_tag', type=str,
              help='''systemTag query parameter.''',
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
def get_tag(obj, pretty_print, beep,
            name,
            additional_info_name_space,
            additional_info_attributes,
            level,
            offset,
            limit,
            size,
            field,
            sort_by,
            order,
            system_tag,
            headers,
            payload,
            active_validation):
    """Returns the tags for given filter criteria.
    """
    spinner = init_spinner(beep=beep)
    start_spinner(spinner)
    try:
        if headers is not None:
            headers = json.loads(headers)
        if payload is not None:
            payload = json.loads(payload)
        result = obj.get_tag(
            name=name,
            additional_info_name_space=additional_info_name_space,
            additional_info_attributes=additional_info_attributes,
            level=level,
            offset=offset,
            limit=limit,
            size=size,
            field=field,
            sort_by=sort_by,
            order=order,
            system_tag=system_tag,
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
