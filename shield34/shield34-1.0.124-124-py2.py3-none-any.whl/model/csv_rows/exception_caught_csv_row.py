import json

from shield34_reporter.model.csv_rows.helpers.exception_desc import ExceptionDesc
from shield34_reporter.model.csv_rows.internal_action_csv_row import InternalActionCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType


class ExceptionCaughtCsvRow(InternalActionCsvRow):


    exceptionType = ''
    exception = None

    def __init__(self, exception, exception_type):
        self.exception = ExceptionDesc(exception)
        self.exceptionType = exception_type
        super(ExceptionCaughtCsvRow, self).__init__(RowSubType.EXCEPTION_CAUGHT)

    def gen_row_value(self, lst=['exceptionType', 'exception']):

        row_value = {}
        for a in lst:
            lst_attr = getattr(self, a)
            if hasattr(lst_attr, 'gen_row_value'):
                row_value[a] = lst_attr.gen_row_value()
            else:
                row_value[a] = lst_attr
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]