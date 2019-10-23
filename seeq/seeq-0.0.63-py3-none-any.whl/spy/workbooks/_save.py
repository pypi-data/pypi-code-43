import os

from seeq.base import system

from ._workbook import Workbook


def save(workbooks, folder=None, *, datasource_map_folder=None, clean=False):
    if not isinstance(workbooks, list):
        workbooks = [workbooks]

    if folder is None:
        folder = os.getcwd()

    if clean:
        system.removetree(folder, keep_top_folder=True)

    datasource_maps = None if datasource_map_folder is None else Workbook.load_datasource_maps(datasource_map_folder)

    for workbook in workbooks:  # type: Workbook
        if not isinstance(workbook, Workbook):
            raise RuntimeError('workbooks argument must be a list of Workbook objects')

        workbook_folder_name = '%s (%s)' % (workbook.name, workbook.id)
        workbook_folder = os.path.join(folder, system.cleanse_filename(workbook_folder_name))

        if datasource_maps is not None:
            workbook.datasource_maps = datasource_maps

        workbook.save(workbook_folder)
