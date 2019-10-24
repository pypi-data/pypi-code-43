import json

from shield34_reporter.model.csv_rows.helpers.exception_desc import ExceptionDesc
from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class TestFailureCsvRow(ReportCsvRow):

    exception = None

    def __init__(self, exception):
        self.rowType = RowType.TEST_STATUS
        self.exception = ExceptionDesc(exception)
        super(TestFailureCsvRow, self).__init__(RowSubType.TEST_FAILURE)

    def gen_row_value(self, lst=['exception']):

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


