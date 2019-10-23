import re

from ...sdk import *

from .. import _common
from .. import _login

from ._workbook import Workbook
from .._common import Status

from . import _workbook


def push(workbooks, *, path=None, label=None, datasource_map_folder=None, use_full_path=False,
         to_original_owner=False, replace_acl=False, override_max_interp=False, errors='raise', quiet=False,
         status=None):
    status = Status.validate(status, quiet)
    _common.validate_errors_arg(errors)

    status.update('Pushing workbooks', Status.RUNNING)

    item_map = dict()

    if not isinstance(workbooks, list):
        workbooks = [workbooks]

    remaining_workbooks = list(workbooks)
    errors_encountered = False

    datasource_maps = None if datasource_map_folder is None else Workbook.load_datasource_maps(datasource_map_folder)

    folder_id = _create_folder_path_if_necessary(path) if path is not None else None

    while len(remaining_workbooks) > 0:
        at_least_one_thing_pushed = False

        dependencies_not_found = list()
        for workbook in remaining_workbooks:  # type: Workbook
            if not isinstance(workbook, Workbook):
                raise RuntimeError('"workbooks" argument contains a non Workbook item: %s' % workbook)

            try:
                status.reset_timer()

                status.df.at[workbook.id, 'ID'] = workbook.id
                status.df.at[workbook.id, 'Name'] = workbook.name
                status.df.at[workbook.id, 'Count'] = 0
                status.df.at[workbook.id, 'Time'] = 0
                status.df.at[workbook.id, 'Result'] = 'Pushing'

                if datasource_maps is not None:
                    workbook.datasource_maps = datasource_maps

                workbook_folder_id = workbook.push_containing_folders(item_map, use_full_path, folder_id,
                                                                      to_original_owner, replace_acl)

                try:
                    workbook.push(folder_id=workbook_folder_id, item_map=item_map, label=label,
                                  to_original_owner=to_original_owner, replace_acl=replace_acl,
                                  override_max_interp=override_max_interp, status=status)

                    at_least_one_thing_pushed = True
                    remaining_workbooks.remove(workbook)
                    status.df.at[workbook.id, 'Result'] = 'Success'

                    if len(workbook.item_errors) > 0:
                        raise RuntimeError(workbook.item_errors_str)

                except _workbook.DependencyNotFound as e:
                    status.df.at[workbook.id, 'Count'] = 0
                    status.df.at[workbook.id, 'Time'] = 0
                    status.df.at[workbook.id, 'Result'] = 'Need dependency: %s' % e.message

                    dependencies_not_found.append(str(e))

            except BaseException as e:
                status.exception(e)

                if errors == 'raise':
                    raise

                status.df.at[workbook.id, 'Result'] = _common.format_exception(e)

        if not at_least_one_thing_pushed:
            if errors == 'raise':
                raise RuntimeError('Could not find the following depended-upon workbooks:\n%s\n'
                                   'Therefore, could not import the following workbooks:\n%s\n' %
                                   ('\n'.join(dependencies_not_found),
                                    '\n'.join([str(workbook) for workbook in workbooks])))

            errors_encountered = True
            break

    if errors_encountered:
        status.update('Errors encountered, look at Result column in returned DataFrame', Status.FAILURE)
    else:
        status.update('Push successful', Status.SUCCESS)

    return status.df


def _create_folder_path_if_necessary(path):
    folders_api = FoldersApi(_login.client)

    workbook_path = re.split(r'\s*>>\s*', path.strip())

    parent_id = None
    folder_id = None
    for i in range(0, len(workbook_path)):
        existing_content_id = None
        content_name = workbook_path[i]
        if parent_id:
            folders = folders_api.get_folders(filter='owner',
                                              folder_id=parent_id,
                                              limit=10000)  # type: FolderOutputListV1
        else:
            folders = folders_api.get_folders(filter='owner',
                                              limit=10000)  # type: FolderOutputListV1

        for content in folders.content:  # type: BaseAclOutput
            if content.type == 'Folder' and content_name == content.name:
                existing_content_id = content.id
                break

        if not existing_content_id:
            folder_input = FolderInputV1()
            folder_input.name = content_name
            folder_input.description = 'Created by Seeq Data Lab'
            folder_input.owner_id = _login.user.id
            folder_input.parent_folder_id = parent_id
            folder_output = folders_api.create_folder(body=folder_input)  # type: FolderOutputV1
            existing_content_id = folder_output.id

        parent_id = existing_content_id
        folder_id = existing_content_id

    return folder_id
