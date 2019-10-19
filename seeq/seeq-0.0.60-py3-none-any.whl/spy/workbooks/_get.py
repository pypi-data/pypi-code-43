import re

import pandas as pd
import numpy as np

from seeq.sdk import *

from .. import _common
from .. import _login


class Workbook:
    pass


class Analysis(Workbook):
    pass


def get_folder(path=None, content_filter='owner', recursive=False):
    return _get_folder(path, content_filter, recursive)


def _get_folder(path_filter, content_filter, recursive, parent_id=None, parent_path=None):
    folders_api = FoldersApi(_login.client)
    results_df = pd.DataFrame()

    path_filter_parts = None
    if path_filter is not None:
        path_filter_parts = re.split(r'\s*>>\s*', path_filter.strip())

    if parent_id is not None:
        folder_output_list = folders_api.get_folders(filter=content_filter,
                                                     folder_id=parent_id,
                                                     limit=10000)  # type: FolderOutputListV1
    else:
        folder_output_list = folders_api.get_folders(filter=content_filter,
                                                     limit=10000)  # type: FolderOutputListV1

    for content in folder_output_list.content:  # type: FolderOutputV1
        if path_filter_parts and content.name != path_filter_parts[0]:
            continue

        if not path_filter_parts:
            results_df = results_df.append({
                'ID': content.id,
                'Type': content.type,
                'Path': parent_path if parent_path else np.nan,
                'Name': content.name,
                'Description': content.type,
                'Access Level': content.access_level
            }, ignore_index=True)

        if content.type == 'Folder' and recursive:
            child_path_filter = None
            if path_filter_parts and len(path_filter_parts) > 1:
                child_path_filter = ' >> '.join(path_filter_parts[1:])

            if parent_path is None:
                new_parent_path = content.name
            else:
                new_parent_path = parent_path + ' >> ' + content.name

            child_results_df = _get_folder(child_path_filter, content_filter, recursive, content.id, new_parent_path)

            results_df = results_df.append(child_results_df,
                                           ignore_index=True)

        return results_df


def _put_analysis():
    pass
