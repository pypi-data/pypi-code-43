import json

from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class TestPassedCsvRow(ReportCsvRow):

    def __init__(self):
        self.rowType = RowType.TEST_STATUS
        super(TestPassedCsvRow, self).__init__(RowSubType.TEST_PASSED)

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps("")]