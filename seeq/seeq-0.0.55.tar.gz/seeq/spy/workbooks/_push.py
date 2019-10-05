import re

import numpy as np
import pandas as pd

from ...sdk import *

from .. import _common
from .. import _login

from ._workbook import Workbook

from . import _workbook


def push(workbooks, *, path=None, label=None, datasource_map_folder=None, errors='raise', quiet=False):
    _common.validate_errors_arg(errors)

    status_df = pd.DataFrame()

    _common.display_status('Pushing workbooks', _common.STATUS_RUNNING, quiet, status_df)

    item_map = dict()

    remaining_workbooks = list(workbooks)
    errors_encountered = False

    datasource_maps = None if datasource_map_folder is None else Workbook.load_datasource_maps(datasource_map_folder)

    while len(remaining_workbooks) > 0:
        at_least_one_thing_pushed = False

        dependencies_not_found = list()
        for workbook in remaining_workbooks:  # type: Workbook
            try:
                timer = _common.timer_start()

                status_df.at[workbook.id, 'ID'] = workbook.id
                status_df.at[workbook.id, 'Path'] = workbook['Path'] if 'Path' in workbook else np.nan
                status_df.at[workbook.id, 'Name'] = workbook.name
                status_df.at[workbook.id, 'Count'] = 0
                status_df.at[workbook.id, 'Time'] = 0
                status_df.at[workbook.id, 'Result'] = 'Pushing'

                folder_id = None
                if path is not None:
                    workbook_folder_path = path
                    if 'Relative Path' in workbook and len(workbook['Relative Path'].strip()) > 0:
                        workbook_folder_path += ' >> ' + workbook['Relative Path']
                    folder_id = _create_folder_path_if_necessary(workbook_folder_path)
                else:
                    if 'Path' in workbook and len(workbook['Path'].strip()) > 0:
                        folder_id = _create_folder_path_if_necessary(workbook['Path'])

                try:
                    if datasource_maps is not None:
                        workbook.datasource_maps = datasource_maps

                    workbook.push(folder_id=folder_id, item_map=item_map, label=label, status=(status_df, timer, quiet))
                    at_least_one_thing_pushed = True
                    remaining_workbooks.remove(workbook)
                    status_df.at[workbook.id, 'Result'] = 'Success'
                except _workbook.DependencyNotFound as e:
                    dependencies_not_found.append(str(e))

            except BaseException as e:
                _common.status_exception(e, status_df, quiet)

                if errors == 'raise':
                    raise

                status_df.at[workbook.id, 'Result'] = _common.format_exception(e)

        if not at_least_one_thing_pushed:
            if errors == 'raise':
                raise RuntimeError('Could not resolve the following dependencies:\n%s\n'
                                   'Therefore, could not import the following workbooks:\n%s\n' %
                                   ('\n'.join(dependencies_not_found),
                                    '\n'.join([str(workbook) for workbook in workbooks])))

            errors_encountered = True
            break

    if errors_encountered:
        _common.display_status(
            'Errors encountered, look at Result column in returned DataFrame',
            _common.STATUS_FAILURE, quiet, status_df)
    else:
        _common.display_status(
            'Push successful',
            _common.STATUS_SUCCESS, quiet, status_df)

    return status_df


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
