from .. import _common
from ._workbook import *
from ... import spy


def pull(workbooks_df, *, include_referenced_workbooks=True, return_status_df=False, errors='raise', quiet=False):
    _common.validate_errors_arg(errors)

    for required_column in ['ID', 'Type', 'Workbook Type']:
        if required_column not in workbooks_df.columns:
            raise RuntimeError('"%s" column must be included in workbooks_df' % required_column)

    status_columns = list()

    for col in ['ID', 'Name', 'Workbook Type']:
        if col in workbooks_df:
            status_columns.append(col)

    workbooks_df = workbooks_df[workbooks_df['Type'] != 'Folder']

    status_df = workbooks_df[status_columns].copy().reset_index(drop=True)
    status_df['Count'] = 0
    status_df['Time'] = 0
    status_df['Result'] = 'Queued'
    status_columns.extend(['Count', 'Time', 'Result'])

    _common.display_status('Pulling workbooks', _common.STATUS_RUNNING, quiet, status_df)

    results = list()
    workbooks_to_pull = dict()
    referencing_search_folder_id = dict()
    original_item_map = dict()
    for index, row in workbooks_df.iterrows():
        item_id = _common.get(row, 'ID')

        try:
            if _common.get(row, 'Workbook Type') == 'Analysis':
                if item_id not in workbooks_to_pull:
                    workbooks_to_pull[item_id] = set()

                continue

            timer = _common.timer_start()
            status_df.at[status_df['ID'] == item_id, 'Result'] = 'Pulling'

            workbook = Item.pull(item_id,
                                 original_item_map=original_item_map,
                                 allowed_types=['Workbook'],
                                 status=(status_df, timer, quiet))  # type: Workbook

            if include_referenced_workbooks and _common.get(row, 'Workbook Type') == 'Topic':
                for workbook_id, workstep_tuple in workbook.referenced_workbooks.items():
                    if workbook_id not in workbooks_to_pull:
                        workbooks_to_pull[workbook_id] = set()
                        if len(status_df[status_df['ID'] == workbook_id]) == 0:
                            search_df = spy.workbooks.search({'ID': workbook_id}, quiet=True)
                            if len(search_df) == 1:
                                search_df['Count'] = 0
                                search_df['Time'] = 0
                                search_df['Result'] = 'Queued'
                                status_df.loc[len(status_df)] = search_df.iloc[0][status_columns]

                    if workstep_tuple not in workbooks_to_pull[workbook_id]:
                        workbooks_to_pull[workbook_id].update(workstep_tuple)
                        referencing_search_folder_id[workbook_id] = _common.get(row, 'Search Folder ID')

            if _common.present(row, 'Search Folder ID'):
                workbook['Search Folder ID'] = _common.get(row, 'Search Folder ID')

            results.append(workbook)

            status_df.at[status_df['ID'] == item_id, 'Time'] = _common.timer_elapsed(timer)
            status_df.at[status_df['ID'] == item_id, 'Result'] = 'Success'

        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                status_df['Result'] = 'Canceled'
                status_message = 'Pull canceled'
                status_code = _common.STATUS_CANCELED
                _common.display_status(status_message, status_code, quiet, status_df)
                return None

            if errors == 'raise':
                raise

            status_df.at[status_df['ID'] == item_id, 'Result'] = _common.format_exception(e)

    for workbook_id, workstep_tuples in workbooks_to_pull.items():
        timer = _common.timer_start()

        try:
            workbook = Item.pull(workbook_id,
                                 original_item_map=original_item_map,
                                 allowed_types=['Workbook'],
                                 status=(status_df, timer, quiet))  # type: Workbook

            workbook.pull_worksteps(list(workstep_tuples))

            workbook_row = workbooks_df[workbooks_df['ID'] == workbook_id]
            if len(workbook_row) == 1 and 'Search Folder ID' in workbook_row.columns:
                workbook['Search Folder ID'] = workbook_row.iloc[0]['Search Folder ID']
            elif workbook_id in referencing_search_folder_id and referencing_search_folder_id[workbook_id] is not None:
                # If the workbook was pulled only as a result of being referenced by something else (like a Topic),
                # we don't have a specific Search Folder ID to use. So just use the search folder ID of the referencing
                # item. (Note: If it's referenced by multiple things, then "last one wins".)
                workbook['Search Folder ID'] = referencing_search_folder_id[workbook_id]

            results.append(workbook)

            status_df.at[status_df['ID'] == workbook_id, 'Time'] = _common.timer_elapsed(timer)
            status_df.at[status_df['ID'] == workbook_id, 'Result'] = 'Success'

        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                status_df['Result'] = 'Canceled'
                status_message = 'Pull canceled'
                status_code = _common.STATUS_CANCELED
                _common.display_status(status_message, status_code, quiet, status_df)
                return None

            if errors == 'raise':
                raise

            status_df.at[status_df['ID'] == workbook_id, 'Result'] = _common.format_exception(e)

    for workbook in results:
        workbook.use_original_ids(original_item_map)

    _common.display_status('Pull successful', _common.STATUS_SUCCESS, quiet, status_df)

    return (results, status_df) if return_status_df else results
