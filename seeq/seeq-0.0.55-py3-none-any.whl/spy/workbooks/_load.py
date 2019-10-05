import os

from .. import _common
from ._workbook import *


def load(folder):
    workbook_json_files = glob.glob(os.path.join(folder, '**', 'Workbook.json'), recursive=True)

    workbooks = list()
    for workbook_json_file in workbook_json_files:
        workbooks.append(Workbook.load(os.path.dirname(workbook_json_file)))

    return workbooks
