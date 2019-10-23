import requests

import pandas as pd

from seeq.sdk43 import *

from .. import _common
from .. import _login

from ...sdk.rest import *
from ...base import gconfig
from .._common import Status


def search(query, *, content_filter='owner', all_properties=False, recursive=False, quiet=False, status=None):
    return _search(query, content_filter=content_filter, all_properties=all_properties, recursive=recursive,
                   quiet=quiet, status=status)


def _search(query, *, content_filter, all_properties, recursive, parent_id=None, parent_path='', search_folder_id=None,
            quiet=False, status=None):
    status = Status.validate(status, quiet)

    items_api = ItemsApi(_login.client)
    users_api = UsersApi(_login.client)
    workbooks_api = WorkbooksApi(_login.client)
    results_df = pd.DataFrame()

    content_filter = content_filter.upper()
    allowed_content_filters = ['OWNER', 'SHARED', 'PUBLIC', 'ALL']
    if content_filter not in allowed_content_filters:
        raise ValueError('content_filter must be one of: %s' % ', '.join(allowed_content_filters))

    for _key, _ in query.items():
        supported_query_fields = ['ID', 'Path', 'Name', 'Description']
        if _key not in supported_query_fields:
            raise RuntimeError('"%s" unsupported query field, use instead one or more of: %s' %
                               (_key, ', '.join(supported_query_fields)))

    def _get_owner_username(_content):
        if 'username' in _content['owner']:
            return _content['owner']['username']
        else:
            user_output = users_api.get_user(id=_content['owner']['id'])  # type: UserOutputV1
            return user_output.username

    if 'ID' in query:
        try:
            workbook_output = workbooks_api.get_workbook(id=query['ID'])  # type: WorkbookOutputV1
        except ApiException as e:
            if e.status == 404:
                return pd.DataFrame()

            raise

        content_dict = {
            'ID': workbook_output.id,
            'Type': workbook_output.type,
            'Workbook Type': _common.get_workbook_type(workbook_output.data),
            'Path': ' >> '.join([a.name for a in workbook_output.ancestors]),
            'Name': workbook_output.name,
            'Owner Name': workbook_output.owner.name,
            'Owner Username': workbook_output.owner.username,
            'Owner ID': workbook_output.owner.id,
            'Pinned': workbook_output.marked_as_favorite,
            'Created At': pd.to_datetime(workbook_output.created_at),
            'Updated At': pd.to_datetime(workbook_output.updated_at),
            'Access Level': workbook_output.access_level
        }

        return pd.DataFrame([content_dict])

    path_filter = query['Path'] if 'Path' in query else None

    path_filter_parts = list()
    if path_filter is not None:
        path_filter_parts = re.split(r'\s*>>\s*', path_filter.strip())

    if len(path_filter_parts) == 0 and search_folder_id is None:
        search_folder_id = parent_id

    if parent_id is not None:
        folder_output_list = _get_folders(content_filter=content_filter,
                                          folder_id=parent_id)
    else:
        folder_output_list = _get_folders(content_filter=content_filter)

    for content in folder_output_list['content']:
        path_matches = False
        props_match = True
        if content['type'] == 'Folder' and len(path_filter_parts) > 0 and \
                _common.does_query_fragment_match(path_filter_parts[0], content['name'], contains=False):
            path_matches = True

        for query_key, content_key in [('Name', 'name'), ('Description', 'description')]:
            if query_key in query and (content_key not in content or
                                       not _common.does_query_fragment_match(query[query_key],
                                                                             content[content_key])):
                props_match = False
                break

        absolute_path = parent_path

        if props_match and len(path_filter_parts) == 0:
            owner_username = _get_owner_username(content)

            content_dict = {
                'ID': content['id'],
                'Type': content['type'],
                'Path': absolute_path,
                'Name': content['name'],
                'Owner Name': content['owner']['name'],
                'Owner Username': owner_username,
                'Owner ID': content['owner']['id'],
                'Pinned': content['markedAsFavorite'],
                'Created At': pd.to_datetime(content['createdAt']),
                'Updated At': pd.to_datetime(content['updatedAt']),
                'Access Level': content['accessLevel']
            }

            if search_folder_id:
                content_dict['Search Folder ID'] = search_folder_id

            if content['type'] != 'Folder':
                content_dict['Workbook Type'] = _common.get_workbook_type(content['data'])

            if all_properties:
                excluded_properties = [
                    # Exclude these because they're in ns-since-epoch when we retrieve them this way
                    'Created At', 'Updated At',

                    # Exclude this because it's a bunch of JSON that will clutter up the DataFrame
                    'Data', 'workbookState'
                ]

                _item = items_api.get_item_and_all_properties(id=content['id'])  # type: ItemOutputV1
                for prop in _item.properties:  # type: PropertyOutputV1

                    if prop.name in excluded_properties:
                        continue

                    content_dict[prop.name] = _common.none_to_nan(prop.value)

            results_df = results_df.append(content_dict, ignore_index=True, sort=True)

        if content['type'] == 'Folder' and ((recursive and len(path_filter_parts) == 0) or path_matches):
            child_path_filter = None
            if path_filter_parts and len(path_filter_parts) > 1:
                child_path_filter = ' >> '.join(path_filter_parts[1:])

            if len(parent_path) == 0:
                new_parent_path = content['name']
            else:
                new_parent_path = parent_path + ' >> ' + content['name']

            child_query = dict(query)
            if not child_path_filter and 'Path' in child_query:
                del child_query['Path']
            else:
                child_query['Path'] = child_path_filter

            child_results_df = _search(child_query, content_filter=content_filter, all_properties=all_properties,
                                       recursive=recursive, parent_id=content['id'], parent_path=new_parent_path,
                                       search_folder_id=search_folder_id, quiet=quiet)

            results_df = results_df.append(child_results_df, ignore_index=True, sort=True)

    return results_df


def _get_folders(content_filter='ALL', folder_id=None, archived=False, sort_order='createdAt ASC', only_pinned=False):
    # We have to make a "raw" REST request here because the get_folders API doesn't work well due to the
    # way it uses inheritance.
    api_client_url = gconfig.get_api_url()
    query_params = 'filter=%s&isArchived=%s&sortOrder=%s&limit=100000&onlyPinned=%s' % (
        content_filter,
        str(archived).lower(),
        sort_order,
        str(only_pinned).lower())

    request_url = api_client_url + '/folders?' + query_params

    if folder_id:
        request_url += '&folderId=' + folder_id

    response = requests.get(request_url, headers={
        "Accept": "application/vnd.seeq.v1+json",
        "x-sq-auth": _login.client.auth_token
    }, verify=Configuration().verify_ssl)

    return json.loads(response.content)
